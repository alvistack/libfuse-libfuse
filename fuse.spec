# Copyright 2025 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

%global _lto_cflags %{?_lto_cflags} -ffat-lto-objects

Name: fuse
Epoch: 100
Version: 2.9.9
Release: 1%{?dist}
Summary: File System in Userspace (FUSE) v2 utilities
License: LGPL-2.1-or-later
URL: https://github.com/libfuse/libfuse/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: fdupes
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: gettext-devel
BuildRequires: libselinux-devel
BuildRequires: libtool
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: systemd-udev
BuildRequires: which
Requires: which
%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
Requires: fuse-common >= 100:3.10.1
Conflicts: fuse-common < 100:3.10.5-1
Conflicts: filesystem < 3
%endif

%description
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v2 userspace tools to
mount a FUSE filesystem.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
ln -fs /usr/share/gettext/config.rpath .
export CFLAGS="%{optflags} -g -fno-strict-aliasing"
export MOUNT_FUSE_PATH=%{_exec_prefix}/sbin
autoreconf -i
%configure
%make_build

%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
%package -n libulockmgr1
Summary: Library of FUSE, the User space File System for GNU/Linux and BSD
Group: System/Filesystems

%description -n libulockmgr1
With FUSE, a user space program can export a file system through the
kernel-default (Linux kernel).

%package -n libfuse2
Summary: Library of FUSE, the User space File System for GNU/Linux and BSD
Group: System/Filesystems

%description -n libfuse2
FUSE (Filesystem in Userspace) is an interface by the Linux kernel
for userspace programs to export a filesystem to the kernel.

A FUSE file system is typically implemented as a standalone
application that links with libfuse. libfuse provides a C API over
the raw kernel interface.

%package doc
Summary: Document package for FUSE (userspace filesystem)
Group: Development/Languages/C and C++

%description doc
This package contains the documentation for FUSE (userspace filesystem).

%package devel
Summary: Development package for FUSE (userspace filesystem) modules
Group: Development/Languages/C and C++
Requires: fuse = %{epoch}:%{version}-%{release}
Requires: fuse-doc = %{epoch}:%{version}-%{release}
Requires: glibc-devel
Requires: libfuse2 = %{epoch}:%{version}-%{release}
Requires: libulockmgr1 = %{epoch}:%{version}-%{release}

%description devel
This package contains all include files, libraries and configuration
files needed to develop programs that use the fuse (FUSE) library to
implement file systems in user space.

With fuse-devel, users can compile and install other user space file
systems.

%package devel-static
Summary: Development package for FUSE (userspace filesystem) modules
Group: Development/Languages/C and C++
Requires: fuse-devel = %{epoch}:%{version}-%{release}
Provides: fuse-devel:%{_libdir}/libfuse.a

%description devel-static
This package contains the static library variants of libfuse.

%install
%make_install
rm -rf %{buildroot}%{_sysconfdir}/init.d
install -m644 -D fuse.conf %{buildroot}%{_sysconfdir}/fuse.conf
# Needed for OpenSUSE buildservice
find %{buildroot} -type f -name "*.la" -delete -print
# not needed for fuse, might reappar in separate package:
rm -f %{buildroot}%{_libdir}/libulockmgr.a
install -m755 -D util/mount.fuse %{buildroot}%{_exec_prefix}/sbin/mount.fuse
pushd %{buildroot}%{_libdir}
ln -fs libfuse.so.%{version} libfuse.so.2
ln -fs libfuse.so.%{version} libfuse.so
ln -fs libulockmgr.so.1.0.1 libulockmgr.so.1
ln -fs libulockmgr.so.1.0.1 libulockmgr.so
popd

(cd example && make clean)
rm -rf example/.deps example/Makefile.am example/Makefile.in
rm -rf doc/Makefile.am doc/Makefile.in doc/Makefile

# Delete pointless udev rules, which do not belong in /usr/lib (brc#748204)
rm -rf %{buildroot}%{_sysconfdir}/udev
fdupes -qnrps doc

%post -n libfuse2 -p /sbin/ldconfig
%postun -n libfuse2 -p /sbin/ldconfig
%post -n libulockmgr1 -p /sbin/ldconfig
%postun -n libulockmgr1 -p /sbin/ldconfig

%files
%license COPYING*
%doc AUTHORS ChangeLog NEWS README*
%verify(not mode) %attr(4750,root,trusted) %{_bindir}/fusermount
%{_exec_prefix}/sbin/mount.fuse
%config %{_sysconfdir}/fuse.conf
%{_bindir}/ulockmgr_server
%{_mandir}/man1/*
%{_mandir}/man8/*

%files -n libfuse2
%{_libdir}/libfuse.so.2*

%files -n libulockmgr1
%{_libdir}/libulockmgr.so.*

%files doc
%doc example doc

%files devel
%{_libdir}/libfuse.so
%{_libdir}/libulockmgr.so
%{_includedir}/fuse.h
%{_includedir}/fuse
%{_libdir}/pkgconfig/*.pc
%{_includedir}/ulockmgr.h

%files devel-static
%{_libdir}/libfuse.a
%endif

%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
%package libs
Summary: File System in Userspace (FUSE) v2 libraries
Conflicts: filesystem < 3

%description libs
Devel With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v2 libraries.

%package devel
Summary: File System in Userspace (FUSE) v2 devel files
Requires: fuse-libs = %{epoch}:%{version}-%{release}
Requires: pkgconfig
Conflicts: filesystem < 3

%description devel
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains development files (headers,
pgk-config) to develop FUSE v2 based applications/filesystems.

%install
mkdir -p %{buildroot}%{_libdir}/pkgconfig
install -m 0755 lib/.libs/libfuse.so.%{version} %{buildroot}%{_libdir}
install -m 0755 lib/.libs/libulockmgr.so.1.0.1 %{buildroot}%{_libdir}
install -p fuse.pc %{buildroot}%{_libdir}/pkgconfig/
mkdir -p %{buildroot}%{_bindir}
install -m 0755 util/fusermount %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_exec_prefix}/sbin
install -m 0755 util/mount.fuse %{buildroot}%{_exec_prefix}/sbin
install -m 0755 util/ulockmgr_server %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_includedir}/fuse
install -p include/old/fuse.h %{buildroot}%{_includedir}/
install -p include/ulockmgr.h %{buildroot}%{_includedir}/
for i in cuse_lowlevel.h fuse_common_compat.h fuse_common.h fuse_compat.h fuse.h fuse_lowlevel_compat.h fuse_lowlevel.h fuse_opt.h; do
	install -p include/$i %{buildroot}%{_includedir}/fuse/
done
mkdir -p %{buildroot}%{_mandir}/man1/
cp -a doc/fusermount.1 doc/ulockmgr_server.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_mandir}/man8/
cp -a doc/mount.fuse.8 %{buildroot}%{_mandir}/man8/
pushd %{buildroot}%{_libdir}
ln -fs libfuse.so.%{version} libfuse.so.2
ln -fs libfuse.so.%{version} libfuse.so
ln -fs libulockmgr.so.1.0.1 libulockmgr.so.1
ln -fs libulockmgr.so.1.0.1 libulockmgr.so
popd

# Get rid of static libs
rm -f %{buildroot}%{_libdir}/*.a

# No need to create init-script
rm -f %{buildroot}%{_sysconfdir}/init.d/fuse

# Delete pointless udev rules, which do not belong in /usr/lib (brc#748204)
rm -rf %{buildroot}usr/lib/udev
fdupes -qnrps doc

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%license COPYING
%doc AUTHORS ChangeLog NEWS README.md README.NFS
%{_exec_prefix}/sbin/mount.fuse
%attr(4755,root,root) %{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%{_mandir}/man1/*
%{_mandir}/man8/*

%files libs
%license COPYING.LIB
%{_libdir}/libfuse.so.*
%{_libdir}/libulockmgr.so.*

%files devel
%{_libdir}/libfuse.so
%{_libdir}/libulockmgr.so
%{_libdir}/pkgconfig/fuse.pc
%{_includedir}/fuse.h
%{_includedir}/ulockmgr.h
%{_includedir}/fuse
%endif

%changelog
