%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global pypi_name murano

%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order pylint os-api-ref
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

Name:          openstack-%{pypi_name}
Version:       XXX
Release:       XXX
Summary:       OpenStack Murano Service

License:       Apache-2.0
URL:           https://pypi.python.org/pypi/murano
Source0:       https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:       openstack-murano-api.service
Source2:       openstack-murano-engine.service
Source3:       openstack-murano.logrotate
Source4:       openstack-murano-cf-api.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:     noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires: git-core
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
BuildRequires: systemd
BuildRequires: openstack-macros

%description
Murano Project introduces an application catalog service

# MURANO-COMMON
%package common
Summary: Murano common
%description common
Components common to all OpenStack Murano services

# MURANO-ENGINE
%package engine
Summary: The Murano engine
Group:   Applications/System
Requires: %{name}-common = %{version}-%{release}

%description engine
OpenStack Murano Engine daemon

# MURANO-API
%package api
Summary: The Murano API
Group:   Applications/System
Requires: %{name}-common = %{version}-%{release}

%description api
OpenStack rest API to the Murano Engine

# MURANO-CF-API
%package cf-api
Summary: The Murano Cloud Foundry API
Group: System Environment/Base
Requires: %{name}-common = %{version}-%{release}

%description cf-api
OpenStack rest API for Murano to the Cloud Foundry

%if 0%{?with_doc}
%package doc
Summary: Documentation for OpenStack Murano services

%description doc
This package contains documentation files for Murano.
%endif

%package -n python3-murano-tests
Summary:        Murano tests
Requires:       %{name}-common = %{version}-%{release}
Requires:       python3-testtools >= 2.2.0

%description -n python3-murano-tests
This package contains the murano test files.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -S git -n %{pypi_name}-%{upstream_version}


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# do not run linters
rm -f murano/tests/unit/test_hacking.py

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%install
%pyproject_install

# Generate sample config files
PYTHONPATH=%{buildroot}/%{python3_sitelib} oslo-config-generator --config-file=./etc/oslo-config-generator/murano.conf
PYTHONPATH=%{buildroot}/%{python3_sitelib} oslo-config-generator --config-file=./etc/oslo-config-generator/murano-cfapi.conf

# Generate i18n files
%{__python3} setup.py compile_catalog -d %{buildroot}%{python3_sitelib}/%{pypi_name}/locale --domain murano


# DOCs
%if 0%{?with_doc}
%tox -e docs
# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo

%endif

mkdir -p %{buildroot}/var/log/murano
mkdir -p %{buildroot}/var/run/murano
mkdir -p %{buildroot}/var/cache/murano/meta
mkdir -p %{buildroot}/etc/murano/
# install systemd unit files
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/murano-api.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/murano-engine.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/murano-cf-api.service
# install logrotate rules
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/murano
# install default config files
cd %{_builddir}/%{pypi_name}-%{upstream_version} && oslo-config-generator --config-file ./etc/oslo-config-generator/murano.conf --output-file %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/murano.conf.sample
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/murano.conf.sample %{buildroot}%{_sysconfdir}/murano/murano.conf
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/netconfig.yaml.sample %{buildroot}%{_sysconfdir}/murano/netconfig.yaml.sample
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/logging.conf.sample %{buildroot}%{_sysconfdir}/murano/logging.conf
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/murano-cfapi.conf.sample %{buildroot}%{_sysconfdir}/murano/murano-cfapi.conf
mv %{buildroot}%{_prefix}/etc/%{pypi_name}/murano-paste.ini %{buildroot}%{_sysconfdir}/%{pypi_name}/murano-paste.ini
mv %{buildroot}%{_prefix}/etc/%{pypi_name}/murano-cfapi-paste.ini %{buildroot}%{_sysconfdir}/%{pypi_name}/murano-cfapi-paste.ini
# Remove duplicate config files under /usr/etc/murano
rmdir %{buildroot}%{_prefix}/etc/%{pypi_name}

# Creating murano core library archive(murano meta packages written in muranoPL with execution plan main minimal logic)
pushd meta/io.murano
zip -r %{buildroot}%{_localstatedir}/cache/murano/meta/io.murano.zip .
popd
pushd meta/io.murano.applications
zip -r %{buildroot}%{_localstatedir}/cache/murano/meta/io.murano.applications.zip .
popd
# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python3_sitelib}/%{pypi_name}/locale/*/LC_*/%{pypi_name}*po
rm -f %{buildroot}%{python3_sitelib}/%{pypi_name}/locale/*pot
mv %{buildroot}%{python3_sitelib}/%{pypi_name}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{pypi_name} --all-name

%check
%tox -e %{default_toxenv}

%files common -f %{pypi_name}.lang
%license LICENSE
%{python3_sitelib}/murano
%{python3_sitelib}/murano-*.dist-info
%exclude %{python3_sitelib}/murano/tests
%exclude %{python3_sitelib}/%{service}_tests.egg-info
%{_bindir}/murano-manage
%{_bindir}/murano-db-manage
%{_bindir}/murano-status
%{_bindir}/murano-test-runner
%{_bindir}/murano-cfapi-db-manage
%dir %attr(0750,murano,root) %{_localstatedir}/log/murano
%dir %attr(0755,murano,root) %{_localstatedir}/run/murano
%dir %attr(0755,murano,root) %{_localstatedir}/cache/murano
%dir %attr(0755,murano,root) %{_sysconfdir}/murano
%config(noreplace) %{_sysconfdir}/logrotate.d/murano
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/murano.conf
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/murano-paste.ini
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/netconfig.yaml.sample
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/logging.conf
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/murano-cfapi.conf
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/murano-cfapi-paste.ini

%pre common
USERNAME=murano
GROUPNAME=$USERNAME
HOMEDIR=/home/$USERNAME
getent group $GROUPNAME >/dev/null || groupadd -r $GROUPNAME
getent passwd $USERNAME >/dev/null || useradd -r -g $GROUPNAME -G $GROUPNAME -d $HOMEDIR -s /sbin/nologin -c "OpenStack Murano Daemons" $USERNAME
exit 0

%files engine
%doc README.rst
%license LICENSE
%{_bindir}/murano-engine
%{_unitdir}/murano-engine.service

%post engine
%systemd_post murano-engine.service

%preun engine
%systemd_preun murano-engine.service

%postun engine
%systemd_postun_with_restart murano-engine.service

%files api
%doc README.rst
%license LICENSE
%{_localstatedir}/cache/murano/*
%{_bindir}/murano-api
%{_bindir}/murano-wsgi-api
%{_unitdir}/murano-api.service

%post api
%systemd_post murano-api.service

%preun api
%systemd_preun murano-api.service

%postun api
%systemd_postun_with_restart murano-api.service

%files cf-api
%doc README.rst
%license LICENSE
%{_bindir}/murano-cfapi
%{_unitdir}/murano-cf-api.service

%post cf-api
%systemd_post murano-cf-api.service

%preun cf-api
%systemd_preun murano-cf-api.service

%postun cf-api
%systemd_postun_with_restart murano-cf-api.service

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc doc/build/html
%endif

%files -n python3-murano-tests
%license LICENSE
%{python3_sitelib}/murano/tests

%changelog
