Summary:	MYSQLSTAT - utilities to monitor, store and display MySQL DBMS usage statistics
Summary(pl.UTF-8):	MYSQLSTAT - narzędzia do monitorowania, zapisywania i wyświetlania statystyk MySQL
Name:		mysqlstat
Version:	0.0.0.4
Release:	10.7
Epoch:		0
License:	GPL
Group:		Applications/Databases
Source0:	http://www.mysqlstat.org/dist/%{name}-%{version}-beta.tar.gz
# Source0-md5:	234035de66c91675362487e55446ed5b
Source1:	%{name}.cron
Source2:	%{name}-apache.conf
Source3:	%{name}-lighttpd.conf
Source4:	%{name}.conf
Patch0:		%{name}-paths.patch
Patch1:		%{name}-logo.patch
Patch2:		%{name}-owner.patch
Patch3:		%{name}-qcache.patch
Patch4:		%{name}-emptypass.patch
Patch5:		%{name}-ndebug.patch
Patch6:		%{name}-mysql-5.0.2.patch
URL:		http://www.mysqlstat.org/en/
BuildRequires:	perl(Fcntl) >= 1.03
BuildRequires:	perl-AppConfig >= 1.52
BuildRequires:	perl-CGI >= 2.752
BuildRequires:	perl-DBD-mysql >= 1.221
BuildRequires:	perl-DBI >= 1.19
BuildRequires:	perl-Digest-MD5 >= 1.19
BuildRequires:	perl-HTML-Template >= 2.5
BuildRequires:	perl-Storable >= 2.04
BuildRequires:	perl-rrdtool >= 1.00
BuildRequires:	rpmbuild(macros) >= 1.264
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires:	crondaemon
Requires:	perl(Fcntl) >= 1.03
Requires:	perl-AppConfig >= 1.52
Requires:	perl-DBD-mysql >= 1.221
Requires:	perl-DBI >= 1.19
Requires:	perl-Storable >= 2.04
Requires:	perl-rrdtool >= 1.00
Provides:	user(mysqlstat)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	/etc/%{name}

%description
MYSQLSTAT - A set of utilities to monitor, store and display MySQL
DBMS usage statistics.

Types of stats:
- Number of queries (queries/sec)
- Number of Connections (conn/sec)
- Data In/Out (bytes/sec)
- Key write requests (requests/sec)
- Key read requests (requests/sec)
- Key writes (writes/sec)
- Key reads (reads/sec)
- Types of queries
- Temporary and disk tables usage

%description -l pl.UTF-8
MYSQLSTAT - zestaw narzędzi do monitorowania, zapisywania i
wyświetlania statystyk systemu baz danych MySQL.

Rodzaje statystyk:
- Liczba zapytań (zapytania/sekundę)
- Liczba połączeń (połączenia/sekundę)
- Wejście/wyjście danych (bajty/sekundę)
- Żądania zapisu klucza (żądania/sekundę)
- Żądania odczytu klucza (żądania/sekundę)
- Zapisy klucza (zapisy/sekundę)
- Odczyty klucza (odczyty/sekundę)
- Rodzaje zapytań
- Wykorzystanie tabel tymczasowych i na dysku

%package cgi
Summary:	MYSQLSTAT - CGI script
Summary(pl.UTF-8):	MYSQLSTAT - skrypt CGI
Group:		Applications/WWW
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	perl-CGI >= 2.752
Requires:	perl-Digest-MD5 >= 1.19
Requires:	perl-HTML-Template >= 2.5
Requires:	webapps
Requires:	webserver
Requires:	webserver(access)
Requires:	webserver(alias)
Requires:	webserver(auth)
Requires:	webserver(cgi)

%description cgi
This package contains the cgi-script for MYSQLSTAT.

%description cgi -l pl.UTF-8
Ten pakiet zawiera skrypt CGI dla programu MYSQLSTAT.

%prep
%setup -q -n %{name}-%{version}-beta
%patch -P0 -p0
%patch -P1 -p0
%patch -P2 -p0
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1

%build
%configure2_13

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/cron.d,%{_datadir}/%{name},/var/{cache,lib}/%{name},%{_webapps}/%{_webapp}}

%{__make} -j1 install \
	BINDEST=$RPM_BUILD_ROOT%{_prefix}/lib/%{name} \
	ETCDEST=$RPM_BUILD_ROOT%{_sysconfdir} \
	CGIBINDEST=$RPM_BUILD_ROOT%{_prefix}/lib/%{name} \
	VARDEST=$RPM_BUILD_ROOT/var/lib/%{name} \
	LIBSDEST=$RPM_BUILD_ROOT%{_prefix}/lib/%{name} \
	HOME=$RPM_BUILD_ROOT%{_datadir}/%{name} \

install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/lighttpd.conf
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%useradd -u 138 -g http -c "MySQL Statistics" mysqlstat

%postun
if [ "$1" = "0" ]; then
	%userremove mysqlstat
fi

%preun cgi
if [ "$1" = "0" ]; then
	rm -f /var/cache/%{name}/* 2>/dev/null
fi

%triggerin cgi -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun cgi -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin cgi -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun cgi -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin cgi -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun cgi -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc %lang(ru) FAQ.RUS README.RUS TODO.RUS
%doc bin/print_data
%dir %attr(700,mysqlstat,root) %{_sysconfdir}
%attr(600,mysqlstat,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/mysqlstat.pm
%attr(755,root,root) %{_prefix}/lib/%{name}/collector
%dir %attr(750,mysqlstat,http) /var/lib/%{name}

%files cgi
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/lighttpd.conf
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%attr(755,root,root) %{_prefix}/lib/%{name}/mysqlstat.cgi
%dir %attr(750,http,http) /var/cache/%{name}
