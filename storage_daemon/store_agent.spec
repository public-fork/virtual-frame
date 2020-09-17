%define name store_agent
%define version %(grep -m1 __version__ storeagent/__init__.py | awk -F = '{print $2}' | sed "s/'//g")
%define python_path /opt/pipenv/.venv/bin/python3


Summary: A gRPC server for store_agent
Name: %{name}
Version: %{version}
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.gz
Autoreq: 0
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: anymous <anymous@example.com>
Url: www.example.com


%description
A gRPC server for system
release tag: %{release_tag}


%prep
%setup -n %{name}-%{version} -n %{name}-%{version}


%build
%{python_path} setup.py build


%install
%{python_path} setup.py install --no-compile --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%{python_path} -m compileall -b legacy $RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name "*.py" 2>/dev/null | xargs rm -rf
sed -i 's#\.py$#\.pyc#g' INSTALLED_FILES

_python_path=%{python_path}
path_prefix=${_python_path%/bin/*}
mkdir -p $RPM_BUILD_ROOT/etc/
mkdir -p $RPM_BUILD_ROOT/opt/storeagent/{conf,json,xml}
mv ${RPM_BUILD_ROOT}${path_prefix}/data/  $RPM_BUILD_ROOT/etc/vap
mv $RPM_BUILD_ROOT/etc/vap/default_multipath.conf $RPM_BUILD_ROOT/opt/storeagent/conf
mv $RPM_BUILD_ROOT/etc/vap/schema.json $RPM_BUILD_ROOT/opt/storeagent/json
sed -i "s#${path_prefix}/data/storeagent\.cfg#/etc/vap/storeagent\.cfg#g" INSTALLED_FILES
sed -i "s#${path_prefix}/data/default_multipath\.conf#/opt/storeagent/conf/default_multipath\.conf#g" INSTALLED_FILES
sed -i "s#${path_prefix}/data/schema\.json#/opt/storeagent/json/schema\.json#g" INSTALLED_FILES
echo "/opt/storeagent/xml/" >> INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system
cp store_agent.service $RPM_BUILD_ROOT/usr/lib/systemd/system/
echo "/usr/lib/systemd/system/store_agent.service" >> INSTALLED_FILES


%preun
if [ $1 -eq 0 ]; then
    # uninstall not upgrade
    systemctl --no-reload disable --now %{name}.service &>/dev/null || :
fi


%postun
if [ $1 -ge 1 ]; then
    # upgrade not uninstall
    systemctl try-restart %{name}.service &>/dev/null || :
fi


%check
find $RPM_BUILD_ROOT -type d -name __pycache__ 2>/dev/null | xargs rm -rf


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
