# TODO
#  - cronjob -- Require: crondaemon? (clamav doesn't depend on it, but should we?)
#  - cron to clean cachedir?

%define	userid	138

Summary:	MYSQLSTAT - utilities to monitor, store and display MySQL DBMS usage statistics
Summary(pl):	MYSQLSTAT - narzêdzia do monitorowania, zapisywania i wy¶wietlania statystyk MySQL
Name:		mysqlstat
Version:	0.0.0.4
Release:	0.19
Epoch:		0
License:	GPL
Group:		Applications/Databases
Source0:	http://www.mysqlstat.org/dist/%{name}-%{version}-beta.tar.gz
# Source0-md5:	234035de66c91675362487e55446ed5b
Source1:	%{name}.cron
Source2:	%{name}.conf
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
Requires:	perl-AppConfig >= 1.52
Requires:	perl-CGI >= 2.752
Requires:	perl-DBI >= 1.19
Requires:	perl-Digest-MD5 >= 1.19
Requires:	perl(Fcntl) >= 1.03
Requires:	perl-HTML-Template >= 2.5
Requires:	perl-DBD-mysql >= 1.221
Requires:	perl-Storable >= 2.04
Requires:	rrdtool >= 1.00
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
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

%package cgi
Summary:	MYSQLSTAT - cgi subpackage
Group:		Applications/WWW
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	webserver

%description cgi
This package contains the cgi-script for MYSQLSTAT.

%prep
%setup -q -n %{name}-%{version}-beta
%patch0 -p0
%patch1 -p0

%build
%configure2_13

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/cron.d,%{_datadir}/%{name},/var/lib/%{name}/cache,/etc/httpd}

%{__make} install \
	BINDEST=$RPM_BUILD_ROOT%{_libdir}/%{name} \
	ETCDEST=$RPM_BUILD_ROOT%{_sysconfdir} \
	CGIBINDEST=$RPM_BUILD_ROOT%{_libdir}/%{name} \
	VARDEST=$RPM_BUILD_ROOT/var/lib/%{name} \
	LIBSDEST=$RPM_BUILD_ROOT%{_libdir}/%{name} \
	MYSQLSTAT_USER=%(id -un) \
	MYSQLSTAT_GROUP=%(id -gn) \

cp -a skins $RPM_BUILD_ROOT%{_datadir}/%{name}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/httpd/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/bin/id -u mysqlstat 2>/dev/null`" ]; then
	if [ "`/bin/id -u mysqlstat`" != %{userid} ]; then
		echo "Error: user mysqlstat doesn't have uid=%{userid}. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u %{userid} -d /usr/share/mysqlstat \
		-s /bin/false -g http -c "MySQL Statistics" mysqlstat
fi

%postun
if [ "$1" = "0" ]; then
	%userremove mysqlstat
fi

%post cgi
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*%{name}.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/%{name}.conf" >> /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
elif [ -d /etc/httpd/httpd.conf ]; then
	ln -sf /etc/httpd/%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

%preun cgi
if [ "$1" = "0" ]; then
	umask 027
	if [ -d /etc/httpd/httpd.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
			/etc/httpd/httpd.conf.tmp
		mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	fi
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc FAQ.RUS README.RUS TODO.RUS

%attr(700,mysqlstat,root) %dir %{_sysconfdir}
%attr(600,mysqlstat,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%dir %attr(750,mysqlstat,http) /var/lib/%{name}

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/mysqlstat.pm
%attr(755,root,root) %{_libdir}/%{name}/collector
%attr(755,root,root) %{_libdir}/%{name}/print_data

%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/cron.d/%{name}

%files cgi
%defattr(644,root,root,755)
%attr(640,root,http) %config(noreplace) %verify(not size mtime md5) /etc/httpd/%{name}.conf
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%attr(755,root,root) %{_libdir}/%{name}/mysqlstat.cgi
%dir %attr(750,http,http) /var/lib/%{name}/cache
