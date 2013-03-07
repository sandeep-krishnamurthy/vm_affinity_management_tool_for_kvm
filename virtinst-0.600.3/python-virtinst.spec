# -*- rpm-spec -*-

%define _version 0.600.3
%define _release 1

%define with_rhel6_defaults 0
%define with_selinux 0

%define with_sbin_compat 0

# End local config

%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

# This macro is used for the continuous automated builds. It just
# allows an extra fragment based on the timestamp to be appended
# to the release. This distinguishes automated builds, from formal
# Fedora RPM builds
%define _extra_release %{?dist:%{dist}}%{?extra_release:%{extra_release}}

%define appname virtinst

%if 0%{?fedora} >= 9 || 0%{?rhel} >= 6
%define with_egg 1
%else
%define with_egg 0
%endif


Summary: Python modules and utilities for installing virtual machines
Name: python-%{appname}
Version: %{_version}
Release: %{_release}%{_extra_release}
Source0: http://virt-manager.org/download/sources/%{appname}/%{appname}-%{version}.tar.gz
License: GPLv2+
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
Url: http://virt-manager.org
Provides: virt-install
Provides: virt-clone
Provides: virt-image
Provides: virt-convert
Requires: libvirt-python >= 0.2.0
Requires: urlgrabber
Requires: libxml2-python
Requires: python-urlgrabber
%if %{with_selinux}
Requires: libselinux-python
%endif
BuildRequires: gettext
BuildRequires: python

%description
virtinst is a module that helps build and install libvirt based virtual
machines. Currently supports KVM, QEmu and Xen virtual machines. Package
includes several command line utilities, including virt-install (build
and install new VMs) and virt-clone (clone an existing virtual machine).

%prep
%setup -q -n %{appname}-%{version}

%build
%if %{with_rhel6_defaults}
%define _rhel6_defaults --rhel6defaults
%endif

python setup.py build \
    %{?_rhel6_defaults}

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install -O1 --root=$RPM_BUILD_ROOT --skip-build

%find_lang %{appname}

%if %{with_sbin_compat}
# Back compat in case people hardcoded old /usr/sbin/virt-install location
mkdir -p $RPM_BUILD_ROOT/%{_sbindir}
ln -s ../bin/virt-install $RPM_BUILD_ROOT/%{_sbindir}/virt-install
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{appname}.lang
%defattr(-,root,root)
%doc README COPYING AUTHORS ChangeLog NEWS doc/image.rng doc/example1.xml
%dir %{python_sitelib}/%{appname}
%dir %{python_sitelib}/virtconv
%{python_sitelib}/%{appname}/*
%{python_sitelib}/virtconv/*
%if %{with_egg}
%{python_sitelib}/%{appname}-*.egg-info
%endif
%{_mandir}/man1/*
%{_mandir}/man5/*
%if %{with_sbin_compat}
%{_sbindir}/virt-install
%endif
%{_bindir}/virt-install
%{_bindir}/virt-clone
%{_bindir}/virt-image
%{_bindir}/virt-convert

%changelog
* Sun Jul 29 2012 Cole Robinson <crobinso@redhat.com> - 0.600.3-1
- virtinst release 0.600.3
- virt-install: Fix --cpuset=auto
- virt-clone: Fix cloning to existing local managed block device

* Sun Jul 08 2012 Cole Robinson <crobinso@redhat.com> - 0.600.2-1
- virtinst release 0.600.2
- virt-install: New --memballoon option (Eiichi Tsukata)
- virt-install: Improved qemu/kvm pseries support (Li Zhang, Qing Lin)
- virt-install: Support setting BIOS path using -boot loader=PATH
- Various bug fixes and improvements

* Tue Jan 31 2012 Cole Robinson <crobinso@redhat.com> - 0.600.1-1
- virt-install: --redir option for usb redirection (Marc-André Lureau)
- virt-install: Advanced --controller support for usb2 (Marc-André
  Lureau)
- Many bug fixes and minor improvments.

* Tue Jul 26 2011 Cole Robinson <crobinso@redhat.com> - 0.600.0-1
- virt-install: Various improvements to enable LXC/container guests:
- New --filesystem option for <filesystem> devices
- New --init option for container <init> path
- New --container option (similar to --paravirt or --hvm)
- virt-install: Make --location  remotely (with latest libvirt)
- virt-install: New --smartcard option for <smartcard> devices
- (Marc-André Lureau)
- virt-install: New --numatune option for building guest <numatune> XML
- virt-install: option to set --disk error_policy=
- virt-install: option to set --disk serial=

* Thu Mar 24 2011 Cole Robinson <crobinso@redhat.com> - 0.500.6-1
- virt-install: --graphics spice now enables spicevmc and qxl
- virt-install: New --disk parameter io=native|threads

* Fri Jan 14 2011 Cole Robinson <crobinso@redhat.com> - 0.500.5-1
- New virt-install --cpu option for configuring CPU model/features
- virt-install --vcpus option can not specify topology and maxvcpus
- New virt-install --graphics option to unify --vnc, --sdl, spice config
- New virt-install --print-xml option to skip install and print XML

* Tue Aug 24 2010 Cole Robinson <crobinso@redhat.com> - 0.500.4-1
- New virt-install --console option for specifying virtio console device
- New virt-install --channel option for specifying guest communication channel
- New virt-install --boot option. Allows setting post-install boot
  order, direct kernel/initrd boot, and enabling boot device menu.
- New virt-install --initrd-inject option, which enables installation
  using a _local_ kickstart file (Colin Walters)

* Wed Mar 24 2010 Cole Robinson <crobinso@redhat.com> - 0.500.3-1
- virt-install: New --watchdog option: configure a virtual watchdog device
- virt-install: New --soundhw option: More flexible sound configuration
                deprecates --sound, though back compat is maintained
- virt-install: New --security option: configure VM security driver settings
- virt-install: New --description option: set a human readable description
- Better OS defaults: Use <video> VGA and <sound> AC97 if supported

* Mon Feb  8 2010 Cole Robinson <crobinso@redhat.com> - 0.500.2-1
- virt-install --autostart option for setting domain autostart flag
- virt-install --host-device now supports values via lsusb and lspci

* Thu Dec  3 2009 Cole Robinson <crobinso@redhat.com> - 0.500.1-1
- virt-install now attempts --os-variant detection by default.
- New --disk option 'format', for creating image formats like qcow2 or vmdk
- Many improvements and bugfixes

* Tue Jul 28 2009 Cole Robinson <crobinso@redhat.com> - 0.500.0-1
- New virt-install device options --serial, --parallel, and --video
- Allow various auth types for libvirt connections (PolicyKit, SASL, ...)
- New virt-clone option --auto-clone: generates all needed input.
- Specify network device model via virt-install --network (Guido Gunther)

* Tue Mar  9 2009 Cole Robinson <crobinso@redhat.com> - 0.400.3-1
- Bug fix release
- virt-install --file was busted
- virt-install --os-type windows was busted for --cdrom installs
- virt-install --os-variant values weren't used if installing from a URL

* Tue Mar  3 2009 Cole Robinson <crobinso@redhat.com> - 0.400.2-1
- virt-install --import option for creating a guest from an existing disk
- virt-install --host-device option for host device passthrough
- virt-clone --original-xml for cloning from an xml file
- virt-install --nonetworks option.

* Mon Jan 26 2009 Cole Robinson <crobinso@redhat.com> - 0.400.1-1
- virt-convert virt-image -> vmx support
- virt-image checksum support
- Improved URL fetching support (Debian Xen, Ubuntu kernel + boot.iso)

* Wed Sep 10 2008 Cole Robinson <crobinso@redhat.com> - 0.400.0-1
- Add virt-convert tool
- Add virt-pack tool
- virt-install --disk option for using/provisioning libvirt storage
- virt-install remote installation support
- virt-install --sound option to add soundcard emulation

* Mon Mar 10 2008 Daniel P. Berrange <berrange@redhat.com> - 0.300.3-1
- Use capabilities XML when installing guests
- Accept RFC compliant NFS uris
- Add --force and --noreboot command line flags
- Use .treeinfo config files for Red Hat distro variants

* Thu Jan 10 2008 Daniel P. Berrange <berrange@redhat.com> - 0.300.2-1
- Escape paths in XML
- Add --cpuset to pin vCPUs at install time
- Automatically set windows guests to localtime
- Improved input validation
- Fix virt-image bugs

* Tue Sep 25 2007 Daniel P. Berrange <berrange@redhat.com> - 0.300.1-1
- Fixed default architecture on 32-bit
- Fixed QEMU guest installs from remote architectures
- Added support for PXE installs of fullyvirtualized guests
- Fixed Fedora distro detection

* Wed Aug 29 2007 Daniel P. Berrange <berrange@redhat.com> - 0.300.0-1
- Updated to 0.300.0
- Added virt-image tool
- Switched to calling virsh console and virt-viewer
- Improved user input validation

* Tue Jul 18 2007 Daniel P. Berrange <berrange@redhat.com> - 0.200.0-1
- Updated to 0.200.0
- Added virt-clone tool
- Added manual pages

* Tue Jun 05 2007 Daniel P. Berrange <berrange@redhat.com> - 0.103.0-1
- Updated to 0.103.0 release
- Fixed module import when using --accelerate
- Fixed detection of RHEL5 client distro
- Fixed default 'network's selection & default URI choice to
  not be Xen specific
- Fixed features XML when using initrd for fullvirt

* Tue Mar 20 2007 Daniel P. Berrange <berrange@redhat.com> - 0.102.0-1
- Updated to 0.102.0 release

* Tue Feb 20 2007 Daniel P. Berrange <berrange@redhat.com> - 0.101.0-1
- Introduce QEMU support & refactored kerne/initrd fetching

* Mon Jan 29 2007 Daniel P. Berrange <berrange@redhat.com> - 0.100.0-1
- Initial generic spec file

