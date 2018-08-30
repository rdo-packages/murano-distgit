%global pypi_name murano

%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%if 0%{?fedora}
%global with_python3 1
%{!?python3_shortver: %global python3_shortver %(%{__python3} -c 'import sys; print(str(sys.version_info.major) + "." + str(sys.version_info.minor))')}
%endif

Name:          openstack-%{pypi_name}
Version:       6.0.0
Release:       1%{?dist}
Summary:       OpenStack Murano Service

License:       ASL 2.0
URL:           https://pypi.python.org/pypi/murano
Source0:       https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#

Source1:       openstack-murano-api.service
Source2:       openstack-murano-engine.service
Source3:       openstack-murano.logrotate
Source4:       openstack-murano-cf-api.service

BuildArch:     noarch

BuildRequires: git
BuildRequires: python2-devel
BuildRequires: python2-setuptools
BuildRequires: python2-jsonschema >= 2.6.0
BuildRequires: python2-keystonemiddleware
BuildRequires: python2-oslo-config
BuildRequires: python2-oslo-db
BuildRequires: python2-oslo-i18n
BuildRequires: python2-oslo-log
BuildRequires: python2-oslo-messaging
BuildRequires: python2-oslo-middleware
BuildRequires: python2-oslo-policy
BuildRequires: python2-oslo-serialization
BuildRequires: python2-oslo-service
BuildRequires: python2-openstackdocstheme
BuildRequires: python2-pbr >= 2.0.0
BuildRequires: python2-routes >= 2.3.1
BuildRequires: python2-sphinx
BuildRequires: python-sphinxcontrib-httpdomain
BuildRequires: python2-castellan
BuildRequires: pyOpenSSL
BuildRequires: systemd
BuildRequires: openstack-macros
# Required to compile translation files
BuildRequires: python2-babel

%description
Murano Project introduces an application catalog service

# MURANO-COMMON
%package common
Summary: Murano common
Requires:      python2-alembic >= 0.9.6
Requires:      python2-babel >= 2.3.4
Requires:      python2-debtcollector >= 1.2.0
Requires:      python2-eventlet >= 0.18.2
Requires:      python2-iso8601 >= 0.1.9
Requires:      python2-jsonpatch >= 1.16
Requires:      python2-jsonschema >= 2.6.0
Requires:      python2-keystonemiddleware >= 4.17.0
Requires:      python2-keystoneauth1 >= 3.4.0
Requires:      python2-kombu >= 1:4.0.0
Requires:      python2-netaddr >= 0.7.18
Requires:      python2-oslo-concurrency >= 3.26.0
Requires:      python2-oslo-config >= 2:5.2.0
Requires:      python2-oslo-context >= 2.19.2
Requires:      python2-oslo-db >= 4.27.0
Requires:      python2-oslo-i18n >= 3.15.3
Requires:      python2-oslo-log >= 3.36.0
Requires:      python2-oslo-messaging >= 5.29.0
Requires:      python2-oslo-middleware >= 3.31.0
Requires:      python2-oslo-policy >= 1.30.0
Requires:      python2-oslo-serialization >= 2.18.0
Requires:      python2-oslo-service >= 1.24.0
Requires:      python2-oslo-utils >= 3.33.0
Requires:      python-paste
Requires:      python-paste-deploy >= 1.5.0
Requires:      python2-pbr >= 2.0.0
Requires:      python2-psutil >= 3.2.2
Requires:      python2-congressclient >= 1.9.0
Requires:      python2-heatclient >= 1.10.0
Requires:      python2-keystoneclient >= 1:3.8.0
Requires:      python2-mistralclient >= 3.1.0
Requires:      python2-muranoclient >= 0.8.2
Requires:      python2-neutronclient >= 6.7.0
Requires:      PyYAML >= 3.10
Requires:      python2-routes >= 2.3.1
Requires:      python-semantic_version >= 2.3.1
Requires:      python2-six >= 1.10.0
Requires:      python2-stevedore >= 1.20.0
Requires:      python2-sqlalchemy >= 1.0.10
Requires:      python2-tenacity >= 4.4.0
Requires:      python-webob >= 1.7.1
Requires:      python2-yaql >= 1.1.3
Requires:      python2-castellan >= 0.16.0
Requires:      python2-cryptography >= 2.1
Requires:      %{name}-doc = %{version}-%{release}

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

%package -n python-murano-tests
Summary:        Murano tests
Requires:       %{name}-common = %{version}-%{release}

%description -n python-murano-tests
This package contains the murano test files.

%prep
%autosetup -S git -n %{pypi_name}-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
%{__python2} setup.py build
# Generate i18n files
%{__python2} setup.py compile_catalog -d build/lib/%{pypi_name}/locale
# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator --config-file=./etc/oslo-config-generator/murano.conf
PYTHONPATH=. oslo-config-generator --config-file=./etc/oslo-config-generator/murano-cfapi.conf

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# DOCs
%if 0%{?with_doc}

export PYTHONPATH=.
SPHINX_DEBUG=1 sphinx-build -b html doc/source doc/build/html
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
rm -f %{buildroot}%{python2_sitelib}/%{pypi_name}/locale/*/LC_*/%{pypi_name}*po
rm -f %{buildroot}%{python2_sitelib}/%{pypi_name}/locale/*pot
mv %{buildroot}%{python2_sitelib}/%{pypi_name}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{pypi_name} --all-name

%files common -f %{pypi_name}.lang
%license LICENSE
%{python2_sitelib}/murano
%{python2_sitelib}/murano-*.egg-info
%exclude %{python2_sitelib}/murano/tests
%exclude %{python2_sitelib}/%{service}_tests.egg-info
%{_bindir}/murano-manage
%{_bindir}/murano-db-manage
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

%files -n python-murano-tests
%license LICENSE
%{python2_sitelib}/murano/tests

%changelog
* Thu Aug 30 2018 RDO <dev@lists.rdoproject.org> 6.0.0-1
- Update to 6.0.0

* Thu Aug 16 2018 RDO <dev@lists.rdoproject.org> 6.0.0-0.1.0rc1
- Update to 6.0.0.0rc1

