# TODO
#  - user mysqlstat? or http
#  - cronjob
#  - apache config
#  - description should say that it's web app?
Summary:	MYSQLSTAT - A set of utilities to monitor, store and display Mysql DBMS usage statistics
Name:		mysqlstat
Version:	0.0.0.4
Release:	0.10
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
Requires:	perl-AppConfig >= 1.52
Requires:	perl-CGI >= 2.752
Requires:	perl-DBI >= 1.19
Requires:	perl-Digest-MD5 >= 1.19
Requires:	perl(Fcntl) >= 1.03
Requires:	perl-HTML-Template >= 2.5
Requires:	perl-DBD-mysql >= 1.221
Requires:	perl-Storable >= 2.04
Requires:	rrdtool >= 1.00
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	_sysconfdir	/etc/%{name}

%description
MYSQLSTAT - A set of utilities to monitor, store and display Mysql
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

%prep
%setup -q -n %{name}-%{version}-beta
%patch0 -p0
%patch1 -p0

%build
%configure2_13

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/%{_datadir}/%{name}

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

%files
%defattr(644,root,root,755)
%doc FAQ.RUS README.RUS TODO.RUS

%attr(700,root,root) %dir %{_sysconfdir}
%attr(600,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%dir %attr(710,root,http) /var/lib/%{name}

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/mysqlstat.pm
%attr(755,root,root) %{_libdir}/%{name}/collector
%attr(755,root,root) %{_libdir}/%{name}/print_data
%attr(755,root,root) %{_libdir}/%{name}/mysqlstat.cgi

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
