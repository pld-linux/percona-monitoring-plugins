# TODO
# - cacti: package other templates:
#   http://www.percona.com/doc/percona-monitoring-plugins/1.1/#templates-for-cacti
# - JMX
# - MongoDB
# - Nginx
# - OpenVZ
# - Unix
# - graceful migrate from cacti-template-mysql (use different paths so old pkg could be kept aside?)
%define		template	mysql
Summary:	MySQL cacti templates
Name:		percona-monitoring-plugins
Version:	1.1.8
Release:	2
License:	GPL v2
Group:		Applications/WWW
Source0:	https://www.percona.com/downloads/%{name}/%{name}-%{version}/source/tarball/%{name}-%{version}.tar.gz
# Source0-md5:	3521b07a7f8d9d2438c52dc21a449dfa
Source1:	config.php
Source2:	ssh_config.php
Patch0:		config.patch
Patch1:		paths.patch
Patch2:		perl.patch
Patch3:		make.patch
URL:		https://www.percona.com/software/database-tools/percona-monitoring-plugins
BuildRequires:	rpmbuild(macros) >= 1.630
BuildRequires:	sed >= 4.0
Requires:	cacti >= 0.8.7g-6
Conflicts:	cacti-spine < 0.8.7e-3
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir		/etc/webapps/cacti
%define		cactidir		/usr/share/cacti
%define		resourcedir		%{cactidir}/resource
%define		scriptsdir		%{cactidir}/scripts
%define		cachedir		/var/cache/cacti/mysql_stats
%define		nagiosplugindir	%{_prefix}/lib/nagios/plugins

%description
This is a set of templates for monitoring MySQL servers with Cacti.

%package -n cacti-template-apache
Summary:	Apache Stats
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	nc
# mark obsoletes so ftp admin knows to remove old src.rpm once this package lands
Obsoletes:	cacti-template-apache < 1.1

%description -n cacti-template-apache
Apache Stats for Cacti (PHP Script Server Version).

%package -n cacti-template-memcached
Summary:	Memcached Cacti Template
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	nc
# mark obsoletes so ftp admin knows to remove old src.rpm once this package lands
Obsoletes:	cacti-template-memcached < 1.1

%description -n cacti-template-memcached
This template provides a host template and associated graphs for
graphing the output of the memcached stats command on individual
memcached installations.

Graphs are provided for Bytes Used with total capacity, Cache Hits and
Misses per second, Current Connections, Items Cached, Inbound and
Outbound Network Traffic (bits per second), and Requests per Second
for both the get and set commands.

%package -n cacti-template-mysql
Summary:	Cacti templates for graphing MySQL
Epoch:		1
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	php(mysqli)

%description -n cacti-template-mysql
This is a set of templates for monitoring MySQL servers with Cacti.

%package -n cacti-template-redis
Summary:	Cacti templates for graphing Redis
Epoch:		1
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
# redis template uses nc
Requires:	nc

%description -n cacti-template-redis
This is a set of templates for monitoring Redis servers with Cacti.

%package -n percona-nagios-plugins
Summary:	Percona Monitoring Plugins for Nagios
Group:		Applications/Databases
Requires:	monitoring-plugin-pmp_check_mongo

%description -n percona-nagios-plugins
Percona Monitoring Plugins for Nagios.

%package -n monitoring-plugin-pmp_check_mongo
Summary:	MongoDB Nagios check script
Group:		Networking
Requires:	python-pymongo >= 3.7.1

%description -n monitoring-plugin-pmp_check_mongo
MongoDB Nagios check script.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%{__sed} -i -e '1i#!/usr/bin/php' cacti/scripts/*.php
chmod a+rx cacti/scripts/*.php
install -d cacti/templates

%{__sed} -i -re '1s;#!/usr/bin/env python(2\.7)?;#!%{__python};' nagios/bin/pmp-*.py
# omit .py extension
for f in nagios/bin/pmp-*.py; do
	normalized=${f%.py}
	mv $f $normalized
done

%build
./make.sh nodocs

cd release/%{name}-%{version}

# rename to include fixed names
for xml in cacti/templates/cacti_host_template_*.xml; do
	normalized=${xml%_0.8.*-sver%{version}.xml}.xml
	mv $xml $normalized
done

# regenerate to make port per source
# https://www.percona.com/doc/percona-monitoring-plugins/1.1/cacti/customizing-templates.html
cd cacti
bin/pmp-cacti-template \
  --script scripts/ss_get_mysql_stats.php definitions/mysql.def \
  --mpds port > templates/cacti_host_template_percona_mysql_server_ht.xml

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sysconfdir},%{resourcedir},%{scriptsdir},%{cachedir}}

cd release/%{name}-%{version}

# NAGIOS
install -d $RPM_BUILD_ROOT%{nagiosplugindir}
install -p nagios/bin/pmp-* $RPM_BUILD_ROOT%{nagiosplugindir}

# CACTI
cd cacti
# tools for modifying templates
# https://www.percona.com/doc/percona-monitoring-plugins/1.1/cacti/customizing-templates.html
cp -p bin/pmp-* $RPM_BUILD_ROOT%{_bindir}
cp -a definitions $RPM_BUILD_ROOT%{resourcedir}

# this is what is needed for mysql templates
install -p scripts/ss_get_mysql_stats.php $RPM_BUILD_ROOT%{scriptsdir}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/ss_get_mysql_stats.php

cp -p templates/cacti_host_template_percona_mysql_server_ht.xml \
	$RPM_BUILD_ROOT%{resourcedir}

# these are additional ssh-based templates (not really using ssh, just the
# interface behaves like ssh)
install -p scripts/ss_get_by_ssh.php $RPM_BUILD_ROOT%{scriptsdir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/ss_get_by_ssh.php

# redis template
cp -p templates/cacti_host_template_percona_redis_server_ht.xml \
	$RPM_BUILD_ROOT%{resourcedir}

# memcached template
cp -p templates/cacti_host_template_percona_memcached_server_ht.xml \
	$RPM_BUILD_ROOT%{resourcedir}

# apache template
cp -p templates/cacti_host_template_percona_apache_server_ht.xml \
	$RPM_BUILD_ROOT%{resourcedir}

%post -n cacti-template-apache
%cacti_import_template %{resourcedir}/cacti_host_template_percona_apache_server_ht.xml

%post -n cacti-template-memcached
%cacti_import_template %{resourcedir}/cacti_host_template_percona_memcached_server_ht.xml

%post -n cacti-template-mysql
%cacti_import_template %{resourcedir}/cacti_host_template_percona_mysql_server_ht.xml

%preun -n cacti-template-mysql
if [ "$1" = 0 ]; then
	echo %{cachedir}/* | xargs rm -f
fi

%post -n cacti-template-redis
%cacti_import_template %{resourcedir}/cacti_host_template_percona_redis_server_ht.xml

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog
%attr(755,root,root) %{_bindir}/pmp-cacti-extract-template
%attr(755,root,root) %{_bindir}/pmp-cacti-graph-defs
%attr(755,root,root) %{_bindir}/pmp-cacti-make-hashes
%attr(755,root,root) %{_bindir}/pmp-cacti-template
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ss_get_by_ssh.php
%attr(755,root,root) %{scriptsdir}/ss_get_by_ssh.php
%dir %{resourcedir}/definitions
%{resourcedir}/definitions/apache.def
%{resourcedir}/definitions/galera.def
%{resourcedir}/definitions/gnu_linux.def
%{resourcedir}/definitions/jmx.def
%{resourcedir}/definitions/memcached.def
%{resourcedir}/definitions/mongodb.def
%{resourcedir}/definitions/mysql.def
%{resourcedir}/definitions/nginx.def
%{resourcedir}/definitions/openvz.def
%{resourcedir}/definitions/rds.def
%{resourcedir}/definitions/redis.def

%files -n cacti-template-apache
%defattr(644,root,root,755)
%{resourcedir}/cacti_host_template_percona_apache_server_ht.xml

%files -n cacti-template-memcached
%defattr(644,root,root,755)
%{resourcedir}/cacti_host_template_percona_memcached_server_ht.xml

%files -n cacti-template-mysql
%defattr(644,root,root,755)
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ss_get_mysql_stats.php
%attr(755,root,root) %{scriptsdir}/ss_get_mysql_stats.php
%{resourcedir}/cacti_host_template_percona_mysql_server_ht.xml
%attr(770,root,http) %dir %{cachedir}

%files -n cacti-template-redis
%defattr(644,root,root,755)
%{resourcedir}/cacti_host_template_percona_redis_server_ht.xml

%files -n percona-nagios-plugins
%defattr(644,root,root,755)
%attr(755,root,root) %{nagiosplugindir}/pmp-check-aws-rds
%attr(755,root,root) %{nagiosplugindir}/pmp-check-lvm-snapshots
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-deadlocks
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-deleted-files
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-file-privs
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-innodb
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-pidfile
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-processlist
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-replication-delay
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-replication-running
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-status
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mysql-ts-count
%attr(755,root,root) %{nagiosplugindir}/pmp-check-pt-table-checksum
%attr(755,root,root) %{nagiosplugindir}/pmp-check-unix-memory

%files -n monitoring-plugin-pmp_check_mongo
%defattr(644,root,root,755)
%attr(755,root,root) %{nagiosplugindir}/pmp-check-mongo
