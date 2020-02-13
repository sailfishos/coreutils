Summary: The GNU core utilities: a set of tools commonly used in shell scripts
Name:    gnu-coreutils
Version: 8.31
Release: 0
License: GPLv3+
Url:     https://git.sailfishos.org/mer-core/coreutils
Source0: ftp://ftp.gnu.org/gnu/coreutils/%{name}-%{version}.tar.bz2
# po files like they are shipped with coreutils-%%{version}
Source100:  po.tar.xz
Source101:  coreutils-DIR_COLORS
Source102:  coreutils-DIR_COLORS.xterm
Source105:  coreutils-colorls.sh
Source106:  coreutils-colorls.csh

#do display processor type for uname -p/-i based on uname(2) syscall
Patch103: coreutils-8.2-uname-processortype.patch
#add note about mkdir --mode behaviour into info documentation(#610559)
Patch107: coreutils-8.4-mkdir-modenote.patch

# sh-utils
#add info about TZ envvar to date manpage
Patch703: sh-utils-2.0.11-dateman.patch
Patch713: coreutils-4.5.3-langinfo.patch

# (sb) lin18nux/lsb compliance - multibyte functionality patch
Patch800: coreutils-i18n.patch
# (sb) lin18nux/lsb compliance - expand/unexpand
Patch801: coreutils-i18n-expand-unexpand.patch
# i18n patch for cut - old version - used
Patch804: coreutils-i18n-cut-old.patch
# The unexpand patch above is not correct. Sent to the patch authors
Patch803: coreutils-i18n-fix-unexpand.patch
#(un)expand - allow multiple files on input - broken by patch 801
Patch805: coreutils-i18n-fix2-expand-unexpand.patch
#(un)expand - test BOM headers
Patch806: coreutils-i18n-un-expand-BOM.patch
# make 'sort -h' work for arbitrary column even when using UTF-8 locales
Patch807: coreutils-i18n-sort-human.patch
# fold: preserve new-lines in mutlibyte text (#1418505)
Patch808: coreutils-i18n-fold-newline.patch

#getgrouplist() patch from Ulrich Drepper.
Patch908: coreutils-getgrouplist.patch

#SELINUX Patch - implements Redhat changes
#(upstream did some SELinux implementation unlike with RedHat patch)
Patch950: coreutils-selinux.patch

# not in Fedora
Patch912: coreutils-overflow.patch

Patch2020: Skip-some-requirements-checks.patch
Patch2021: Do-not-fail-on-ENOENT-on-sb2.patch
Patch2022: docs-should-say-var-run-uw-tmp-not-etc-uw-tmp.patch

# For acl support
BuildRequires: libacl-devel
# For xattrs
BuildRequires: libattr-devel
# Other build requirements
BuildRequires: gettext-devel >= 0.19.2
BuildRequires: bison
# This really wants makeinfo >= 6.1 but we don't have it
BuildRequires: texinfo >= 4.3
BuildRequires: autoconf >= 2.64
BuildRequires: automake >= 1.11.2
BuildRequires: gperf
BuildRequires: bash, gzip, tar, xz
BuildRequires: perl >= 5.5

Provides: mktemp
Provides: fileutils = %{version}-%{release}
Provides: sh-utils = %{version}-%{release}
Provides: stat = %{version}-%{release}
Provides: textutils = %{version}-%{release}
Obsoletes: fileutils <= 4.1.9
Obsoletes: sh-utils <= 2.0.12
Obsoletes: stat <= 3.3
Obsoletes: textutils <= 2.0.21

Provides: coreutils = 1:6.9+git1
Obsoletes: coreutils < 1:6.9+git1

%description
These are the GNU core utilities.  This package is the combination of
the old GNU fileutils, sh-utils, and textutils packages.

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}
Obsoletes: coreutils-doc < 1:6.9+git1

%description doc
Man and info pages for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

echo -n %{version} | cut -d+ -f1 > .tarball-version

./bootstrap --no-git --gnulib-srcdir=gnulib --skip-po --no-bootstrap-sync

# Extract po files, usually these would be downloaded by bootstrap
# but we don't have that luxury (no internet access while %preping)
xz -cd %SOURCE100 | tar x

(echo ">>> Fixing permissions on tests") 2>/dev/null
find tests -name '*.sh' -perm 0644 -print -exec chmod 0755 '{}' '+'
(echo "<<< done") 2>/dev/null

%build
export CFLAGS="$RPM_OPT_FLAGS -fpic -D_FILE_OFFSET_BITS=64"
%{expand:%%global optflags %{optflags} -D_GNU_SOURCE=1}

%configure --without-gmp --without-openssl --without-selinux --without-libcap \
           --enable-no-install-program=kill,uptime,stdbuf \
           DEFAULT_POSIX2_VERSION=200112 alternative=199209 \
           TIME_T_32_BIT_OK=yes

make all %{?_smp_mflags}

# make sure that parse-datetime.{c,y} ends up in debuginfo (#1555079)
ln -vf lib/parse-datetime.{c,y} .

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

# man pages are not installed with make install
make mandir=$RPM_BUILD_ROOT%{_mandir} install-man

# The condition is for quick local rebuilds
[ ! -e ChangeLog.bz2 ] && bzip2 -9f ChangeLog

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p $RPM_BUILD_ROOT{/bin,%_bindir,%_sbindir,/sbin}
for f in basename cat chgrp chmod chown cp cut date dd df echo env false link ln ls mkdir mknod mktemp mv nice pwd rm rmdir sleep sort stty sync touch true uname unlink
do
    mv $RPM_BUILD_ROOT{%_bindir,/bin}/$f
done

# chroot was in /usr/sbin :
mv $RPM_BUILD_ROOT{%_bindir,%_sbindir}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into
for i in env cut; do ln -sf ../../bin/$i $RPM_BUILD_ROOT/usr/bin; done

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
install -p -c -m644 %SOURCE101 $RPM_BUILD_ROOT%{_sysconfdir}/DIR_COLORS
install -p -c -m644 %SOURCE102 $RPM_BUILD_ROOT%{_sysconfdir}/DIR_COLORS.xterm
install -p -c -m644 %SOURCE105 $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/colorls.sh
install -p -c -m644 %SOURCE106 $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/colorls.csh

%find_lang coreutils
mv coreutils.lang %{name}.lang

# (sb) Deal with Installed (but unpackaged) file(s) found
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

# Documentation
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} \
        AUTHORS ChangeLog.bz2 NEWS README TODO

%lang_package

%files
%defattr(-,root,root,-)
%{_sysconfdir}/DIR_COLORS*
%{_sysconfdir}/profile.d/*
%license COPYING
/bin/basename
/bin/cat
/bin/chgrp
/bin/chmod
/bin/chown
/bin/cp
/bin/cut
/bin/date
/bin/dd
/bin/df
/bin/echo
/bin/env
/bin/false
/bin/link
/bin/ln
/bin/ls
/bin/mkdir
/bin/mknod
/bin/mv
/bin/nice
/bin/pwd
/bin/rm
/bin/rmdir
/bin/sleep
/bin/sort
/bin/stty
/bin/sync
/bin/touch
/bin/true
/bin/uname
/bin/unlink
/bin/mktemp
%_bindir/*
%_sbindir/chroot

%files doc
%defattr(-,root,root,-)
%{_infodir}/coreutils.info.gz
%{_mandir}/man1/*
%{_docdir}/%{name}-%{version}
