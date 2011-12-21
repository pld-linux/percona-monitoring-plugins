# TODO
# - how to package other ssh based templates?
# - Apache
# - JMX
# - Memcached
# - MongoDB
# - Nginx
# - OpenVZ
# - Unix
# https://code.google.com/p/mysql-cacti-templates/wiki/TableOfContents>
# - currently ss_get_by_ssh.php packaged in -redis package, as it's the only user of it_
%define		template	mysql
Summary:	MySQL cacti templates
Name:		cacti-template-%{template}
Version:	1.1.8
Release:	1.1
License:	GPL v2
Group:		Applications/WWW
Source0:	http://mysql-cacti-templates.googlecode.com/files/better-cacti-templates-%{version}.tar.gz
# Source0-md5:	c34e66af5091bc02b081a446dbe87f53
Source1:	config.php
Source2:	ssh_config.php
Patch0:		config.patch
Patch1:		paths.patch
URL:		http://code.google.com/p/mysql-cacti-templates/
BuildRequires:	rpmbuild(macros) >= 1.554
Requires:	cacti >= 0.8.7g-6
Conflicts:	cacti-spine < 0.8.7e-3
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir		/etc/webapps/cacti
%define		cactidir		/usr/share/cacti
%define		resourcedir		%{cactidir}/resource
%define		scriptsdir		%{cactidir}/scripts
%define		cachedir		/var/cache/cacti/mysql_stats

%description
This is a set of templates for monitoring MySQL servers with Cacti.

%package -n cacti-template-redis
Summary:	Cacti templates for graphing Redis
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
# redis template uses nc
Requires:	nc

%description -n cacti-template-redis
This is a set of templates for monitoring Redis servers with Cacti.

%prep
%setup -qn better-cacti-templates-%{version}
%patch0 -p1
%patch1 -p1

# rename to include fixed names
for xml in templates/cacti_host_template_x_*.xml; do
	normalized=${xml%_0.8.*-sver%{version}.xml}.xml
	mv $xml $normalized
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{resourcedir},%{scriptsdir},%{cachedir}}

# this is what is needed for mysql templates
install -p scripts/ss_get_mysql_stats.php $RPM_BUILD_ROOT%{scriptsdir}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/ss_get_mysql_stats.php

cp -p templates/cacti_host_template_x_mysql_server_ht.xml \
	$RPM_BUILD_ROOT%{resourcedir}

# these are additional ssh-based templates (not really using ssh, just the
# interface behaves like ssh)
install -p scripts/ss_get_by_ssh.php $RPM_BUILD_ROOT%{scriptsdir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/ss_get_by_ssh.php

# redis template
cp -p templates/cacti_host_template_x_redis_server_ht.xml \
	$RPM_BUILD_ROOT%{resourcedir}

%post
%cacti_import_template %{resourcedir}/cacti_host_template_x_mysql_server_ht.xml

%preun
if [ "$1" = 0 ]; then
	echo %{cachedir}/* | xargs rm -f
fi

%post -n cacti-template-redis
%cacti_import_template %{resourcedir}/cacti_host_template_x_redis_server_ht.xml

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING README Changelog
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ss_get_mysql_stats.php
%attr(755,root,root) %{scriptsdir}/ss_get_mysql_stats.php
%{resourcedir}/cacti_host_template_x_mysql_server_ht.xml
%attr(770,root,http) %dir %{cachedir}

%files -n cacti-template-redis
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ss_get_by_ssh.php
%attr(755,root,root) %{scriptsdir}/ss_get_by_ssh.php
%{resourcedir}/cacti_host_template_x_redis_server_ht.xml
