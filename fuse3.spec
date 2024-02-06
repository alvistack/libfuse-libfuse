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

Name: fuse3
Epoch: 100
Version: 3.16.2
Release: 1%{?dist}
Summary: File System in Userspace (FUSE) v3 utilities
License: LGPL-2.1-or-later
URL: https://github.com/libfuse/libfuse/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libselinux-devel
BuildRequires: libtool
BuildRequires: meson
BuildRequires: ninja-build
BuildRequires: pkgconfig
BuildRequires: systemd-udev
BuildRequires: which
Requires: which
%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
Requires: fuse-common >= %{epoch}:%{version}-%{release}
Conflicts: fuse-common < %{epoch}:%{version}-%{release}
Conflicts: filesystem < 3
%endif

%description
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v3 userspace tools to
mount a FUSE filesystem.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%meson
(
    cd %{_vpath_builddir}
    meson configure -D sbindir=%{_exec_prefix}/sbin
    meson configure -D b_lto=false
    meson configure -D b_lundef=false
    meson configure -D examples=false
    meson configure -D useroot=false
    ninja reconfigure
)
%meson_build

%check
readelf -Ws %{_vpath_builddir}/lib/*.so | grep "fuse_parse_cmdline@*FUSE_3.0"

%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
%package -n libfuse3-3
Summary: Library of FUSE, the User space File System for GNU/Linux and BSD

%description -n libfuse3-3
FUSE (Filesystem in Userspace) is an interface by the Linux kernel
for userspace programs to export a filesystem to the kernel.

A FUSE file system is typically implemented as a standalone
application that links with libfuse. libfuse provides a C API over
the raw kernel interface.

%package doc
Summary: Documentation for the FUSE library version 3

%description doc
This package contains the documentation for FUSE (userspace filesystem).

%package devel
Summary: Development package for FUSE (userspace filesystem) modules
Requires: fuse3 = %{epoch}:%{version}-%{release}
Requires: glibc-devel
Requires: libfuse3-3 = %{epoch}:%{version}-%{release}

%description devel
This package contains all include files, libraries and configuration
files needed to develop programs that use the fuse (FUSE) library to
implement file systems in user space.

With fuse-devel, users can compile and install other user space file
systems.

%install
%meson_install

find %{buildroot} -type f -name "*.la" -delete -print

# Remove unneeded stuff
rm -rfv %{buildroot}/%{_prefix}/lib/udev %{buildroot}/%{_sysconfdir}/init.d
fdupes -qnrps doc

%post
%set_permissions %{_bindir}/fusermount3

%verifyscript
%verify_permissions -e %{_bindir}/fusermount3

%post -n libfuse3-3 -p /sbin/ldconfig
%postun -n libfuse3-3 -p /sbin/ldconfig

%files
%license LICENSE GPL2.txt LGPL2.txt
%doc AUTHORS ChangeLog.rst
%verify(not mode) %attr(4750,root,trusted) %{_bindir}/fusermount3
%{_exec_prefix}/sbin/mount.fuse3
%config %{_sysconfdir}/fuse.conf
%{_mandir}/man1/fusermount3.1%{?ext_man}
%{_mandir}/man8/mount.fuse3.8%{?ext_man}

%files -n libfuse3-3
%{_libdir}/libfuse3.so.3*

%files doc
%doc example doc

%files devel
%{_libdir}/libfuse3.so
%{_includedir}/fuse3/*.h
%{_includedir}/fuse3
%{_libdir}/pkgconfig/*.pc
%endif

%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
%package libs
Summary: File System in Userspace (FUSE) v3 libraries

%description libs
Devel With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v3 libraries.

%package devel
Summary: File System in Userspace (FUSE) v3 devel files
Requires: fuse3-libs = %{epoch}:%{version}-%{release}
Requires: pkgconfig

%description devel
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains development files (headers,
pgk-config) to develop FUSE v3 based applications/filesystems.

%package -n fuse-common
Summary: Common files for File System in Userspace (FUSE) v2 and v3

%description -n fuse-common
Common files for FUSE v2 and FUSE v3.

%install
export MESON_INSTALL_DESTDIR_PREFIX=%{buildroot}/usr %meson_install
find %{buildroot} .
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'
# change from 4755 to 0755 to allow stripping -- fixed later in files
chmod 0755 %{buildroot}/%{_bindir}/fusermount3

# Get rid of static libs
rm -f %{buildroot}/%{_libdir}/*.a
# No need to create init-script
rm -f %{buildroot}%{_sysconfdir}/init.d/fuse3

# Install config-file
mkdir -p %{buildroot}%{_sysconfdir}
install -p -m 0644 fuse.conf %{buildroot}%{_sysconfdir}/

# Delete pointless udev rules, which do not belong in /usr/lib (brc#748204)
rm -rf %{buildroot}/usr/lib/udev
fdupes -qnrps doc

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%license LICENSE GPL2.txt
%doc AUTHORS ChangeLog.rst README.md
%attr(4755,root,root) %{_bindir}/fusermount3
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_exec_prefix}/sbin/mount.fuse3

%files libs
%license LGPL2.txt
%{_libdir}/libfuse3.so.*

%files devel
%{_includedir}/fuse3/
%{_libdir}/libfuse3.so
%{_libdir}/pkgconfig/fuse3.pc

%files -n fuse-common
%config(noreplace) %{_sysconfdir}/fuse.conf
%endif

%changelog