%define		template	mysql
Summary:	MySQL cacti templates
Name:		cacti-template-%{template}
Version:	1.1.7
Release:	2
License:	GPL v2
Group:		Applications/WWW
Source0:	http://mysql-cacti-templates.googlecode.com/files/better-cacti-templates-%{version}.tar.gz
# Source0-md5:	cec81aa5cba180d079122127bde9bae0
Source1:	config.php
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

%description
This is a set of templates for monitoring MySQL servers with Cacti.

%prep
%setup -qn better-cacti-templates-%{version}
%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{resourcedir},%{scriptsdir}}

# we deliberately are not packaging other templates this project offers:
# - it's idiotic to graph network services over ssh
# - they should get their own package to avoid some confusion when searching for
#   templates in package repository
install -p scripts/ss_get_mysql_stats.php $RPM_BUILD_ROOT%{scriptsdir}
cp -a templates/cacti_host_template_x_mysql_server*.xml \
	$RPM_BUILD_ROOT%{resourcedir}/cacti_host_template_x_mysql_server.xml
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/ss_get_mysql_stats.php

%post
%cacti_import_template %{resourcedir}/cacti_host_template_x_mysql_server.xml

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING README Changelog
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ss_get_mysql_stats.php
%attr(755,root,root) %{scriptsdir}/ss_get_mysql_stats.php
%{resourcedir}/*.xml
