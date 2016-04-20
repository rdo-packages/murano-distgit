%global pypi_name murano

%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%if 0%{?fedora}
%global with_python3 1
%{!?python3_shortver: %global python3_shortver %(%{__python3} -c 'import sys; print(str(sys.version_info.major) + "." + str(sys.version_info.minor))')}
%endif

Name:          openstack-%{pypi_name}
Version:       2.0.0
Release:       1%{?dist}
Summary:       OpenStack Murano Service

License:       ASL 2.0
URL:           https://pypi.python.org/pypi/murano
Source0:       https://pypi.python.org/packages/source/m/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
Source1:       openstack-murano-api.service
Source2:       openstack-murano-engine.service
Source3:       openstack-murano.logrotate
Source4:       openstack-murano-cf-api.service

BuildArch:     noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-jsonschema >= 2.0.0
BuildRequires: python-keystonemiddleware
BuildRequires: python-oslo-config
BuildRequires: python-oslo-db
BuildRequires: python-oslo-i18n
BuildRequires: python-oslo-log
BuildRequires: python-oslo-messaging
BuildRequires: python-oslo-middleware
BuildRequires: python-oslo-policy
BuildRequires: python-oslo-serialization
BuildRequires: python-oslo-service
BuildRequires: python-oslo-sphinx
BuildRequires: python-pbr >= 1.8
BuildRequires: python-routes >= 1.12.3
BuildRequires: python-sphinx
BuildRequires: python-sphinxcontrib-httpdomain
BuildRequires: pyOpenSSL
BuildRequires: systemd

%description
Murano Project introduces an application catalog service

# MURANO-COMMON
%package common
Summary: Murano common
Requires:      python-alembic >= 0.8.0
Requires:      python-babel >= 1.3
Requires:      python-eventlet >= 0.17.4
Requires:      python-iso8601 >= 0.1.9
Requires:      python-jsonpatch >= 1.1
Requires:      python-jsonschema >= 2.0.0
Requires:      python-keystonemiddleware >= 2.0.0
Requires:      python-kombu >= 3.0.7
Requires:      python-netaddr >= 0.7.12
Requires:      python-oslo-config >= 2:2.3.0
Requires:      python-oslo-context >= 0.2.0
Requires:      python-oslo-db >= 2.4.1
Requires:      python-oslo-i18n >= 1.5.0
Requires:      python-oslo-log >= 1.8.0
Requires:      python-oslo-messaging >= 1.16.0
Requires:      python-oslo-middleware >= 2.8.0
Requires:      python-oslo-policy >= 0.5.0
Requires:      python-oslo-serialization >= 1.4.0
Requires:      python-oslo-service >= 0.7.0
Requires:      python-oslo-utils >= 2.0.0
Requires:      python-paste
Requires:      python-paste-deploy >= 1.5.0
Requires:      python-pbr >= 1.6
Requires:      python-psutil >= 1.1.1
Requires:      python-congressclient >= 1.0.0
Requires:      python-heatclient >= 0.3.0
Requires:      python-keystoneclient >= 1:1.6.0
Requires:      python-mistralclient >= 1.0.0
Requires:      python-muranoclient >= 0.7.0
Requires:      python-neutronclient >= 2.6.0
Requires:      PyYAML >= 3.1.0
Requires:      python-retrying >= 1.2.3
Requires:      python-routes >= 1.12.3
Requires:      python-semantic_version >= 2.3.1
Requires:      python-six >= 1.9.0
Requires:      python-stevedore >= 1.5.0
Requires:      python-sqlalchemy >= 0.9.9
Requires:      python-webob >= 1.2.3
Requires:      python-yaql >= 1.0.0
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

%prep
%autosetup -n %{pypi_name}-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

%build
%{__python2} setup.py build
# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator --config-file=./etc/oslo-config-generator/murano.conf

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# DOCs
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo
%endif

popd

mkdir -p %{buildroot}/var/log/murano
mkdir -p %{buildroot}/var/run/murano
mkdir -p %{buildroot}/var/cache/murano
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
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/murano-paste.ini %{buildroot}%{_sysconfdir}/murano/murano-paste.ini
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/policy.json %{buildroot}%{_sysconfdir}/murano/policy.json
install -p -D -m 640 %{_builddir}/%{pypi_name}-%{upstream_version}/etc/murano/logging.conf.sample %{buildroot}%{_sysconfdir}/murano/logging.conf

# Copy 'meta' folder(murano meta packages written in muranoPL with execution plan main minimal logic)
cp -r %{_builddir}/%{pypi_name}-%{upstream_version}/meta %{buildroot}%{_localstatedir}/cache/murano
zip -r %{buildroot}%{_localstatedir}/cache/murano/meta/io.murano.zip .

%files common
%license LICENSE
%{python2_sitelib}/murano*
%{_bindir}/murano-manage
%{_bindir}/murano-db-manage
%{_bindir}/murano-test-runner
%dir %attr(0755,murano,root) %{_localstatedir}/log/murano
%dir %attr(0755,murano,root) %{_localstatedir}/run/murano
%dir %attr(0755,murano,root) %{_localstatedir}/cache/murano
%dir %attr(0755,murano,root) %{_sysconfdir}/murano
%config(noreplace) %{_sysconfdir}/logrotate.d/murano
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/murano.conf
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/murano-paste.ini
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/netconfig.yaml.sample
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/policy.json
%config(noreplace) %attr(-, root, murano) %{_sysconfdir}/murano/logging.conf

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
%{_localstatedir}/cache/murano
%{_bindir}/murano-api
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

%files doc
%doc doc/build/html

%changelog
* Wed Apr 20 2016 Haikel Guemar <hguemar@fedoraproject.org> 2.0.0-1
- Update to 2.0.0

* Wed Jan 13 2016 2015 Marcos Fermin Lobo <marcos.fermin.lobo@cern.ch> - 0.1.0-1
- First RPM

* Tue Jan 12 2016 Daniil <asteroid566@gmail.com> - 0.1.0-0
- Start spec file and services files
