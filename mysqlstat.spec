# TODO
#  - cronjob
#  - apache config
#  - not sure if requirement for group(http) is really only way, because the
#    statistics gather part really doesn't need web server

%define	userid	138

Summary:	MYSQLSTAT - utilities to monitor, store and display MySQL DBMS usage statistics
Summary(pl):	MYSQLSTAT - narzêdzia do monitorowania, zapisywania i wy¶wietlania statystyk MySQL
Name:		mysqlstat
Version:	0.0.0.4
Release:	0.11
Epoch:		0
License:	GPL
Group:		Applications/Databases
Source0:	http://www.mysqlstat.org/dist/%{name}-%{version}-beta.tar.gz
# Source0-md5:	234035de66c91675362487e55446ed5b
Patch0:		%{name}-paths.patch
Patch1:		%{name}-logo.patch
URL:		http://www.mysqlstat.org/en/
BuildRequires:	perl-AppConfig >= 1.52
BuildRequires:	perl-CGI >= 2.752
BuildRequires:	perl-DBI >= 1.19
BuildRequires:	perl-Digest-MD5 >= 1.19
BuildRequires:	perl(Fcntl) >= 1.03
BuildRequires:	perl-HTML-Template >= 2.5
BuildRequires:	perl-DBD-mysql >= 1.221
BuildRequires:	perl-Storable >= 2.04
BuildRequires:	rrdtool >= 1.00
BuildRequires:	rpmbuild(macros) >= 1.159
Requires:	group(http)
Requires:	perl-AppConfig >= 1.52
Requires:	perl-CGI >= 2.752
Requires:	perl-DBI >= 1.19
Requires:	perl-Digest-MD5 >= 1.19
Requires:	perl(Fcntl) >= 1.03
Requires:	perl-HTML-Template >= 2.5
Requires:	perl-DBD-mysql >= 1.221
Requires:	perl-Storable >= 2.04
Requires:	rrdtool >= 1.00
Provides:	user(mysqlstat)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	_sysconfdir	/etc/%{name}

%description
MYSQLSTAT - A set of utilities to monitor, store and display MySQL
DBMS usage statistics.

Types of stats: 
1. Number of queries (queries/sec) 
2. Number of Connections (conn/sec) 
3. Data In/Out (bytes/sec) 
4. Key write requests (requests/sec) 
5. Key read requests (requests/sec) 
6. Key writes (writes/sec) 
7. Key reads (reads/sec) 
8. Types of queries 
9. Temporary and disk tables usage 

%description -l pl
MYSQLSTAT - zestaw narzêdzi do monitorowania, zapisywania i
wy¶wietlania statystyk systemu baz danych MySQL.

Rodzaje statystyk:
1. Liczba zapytañ (zapytania/sekundê)
2. Liczba po³±czeñ (po³±czenia/sekundê)
3. Wej¶cie/wyj¶cie danych (bajty/sekundê)
4. ¯±dania zapisu klucza (¿±dania/sekundê)
5. ¯±dania odczytu klucza (¿±dania/sekundê)
6. Zapisy klucza (zapisy/sekundê)
7. Odczyty klucza (odczyty/sekundê)
8. Rodzaje zapytañ
9. Wykorzystanie tabel tymczasowych i na dysku

%prep
%setup -q -n %{name}-%{version}-beta
%patch0 -p0
%patch1 -p0

%build
%configure2_13

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}

%{__make} install \
	BINDEST=$RPM_BUILD_ROOT%{_libdir}/%{name} \
	ETCDEST=$RPM_BUILD_ROOT%{_sysconfdir} \
	CGIBINDEST=$RPM_BUILD_ROOT%{_libdir}/%{name} \
	VARDEST=$RPM_BUILD_ROOT/var/lib/%{name} \
	LIBSDEST=$RPM_BUILD_ROOT%{_libdir}/%{name} \
	MYSQLSTAT_USER=%(id -un) \
	MYSQLSTAT_GROUP=%(id -gn) \

cp -a skins $RPM_BUILD_ROOT%{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
[ "`/bin/id -u mysqlstat 2>/dev/null`" ] || \
	/usr/sbin/useradd -u %{userid} -d /usr/share/mysqlstat \
		-s /bin/false -g http -c "MySQL Statistics" mysqlstat

%postun
if [ "$1" = "0" ]; then
    %userremove mysqlstat
fi

%files
%defattr(644,root,root,755)
%doc FAQ.RUS README.RUS TODO.RUS

%attr(700,mysqlstat,root) %dir %{_sysconfdir}
%attr(600,mysqlstat,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%dir %attr(710,mysqlstat,http) /var/lib/%{name}

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/mysqlstat.pm
%attr(755,root,root) %{_libdir}/%{name}/collector
%attr(755,root,root) %{_libdir}/%{name}/print_data
%attr(755,root,root) %{_libdir}/%{name}/mysqlstat.cgi

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
