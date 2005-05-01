# TODO
#  - cronjob -- Require: crondaemon? (clamav doesn't depend on it, but should we?)

%define	userid	138

Summary:	MYSQLSTAT - utilities to monitor, store and display MySQL DBMS usage statistics
Summary(pl):	MYSQLSTAT - narzêdzia do monitorowania, zapisywania i wy¶wietlania statystyk MySQL
Name:		mysqlstat
Version:	0.0.0.4
Release:	2.11
Epoch:		0
License:	GPL
Group:		Applications/Databases
Source0:	http://www.mysqlstat.org/dist/%{name}-%{version}-beta.tar.gz
# Source0-md5:	234035de66c91675362487e55446ed5b
Source1:	%{name}.cron
Source2:	%{name}-apache.conf
Source3:	%{name}.conf
Patch0:		%{name}-paths.patch
Patch1:		%{name}-logo.patch
Patch2:		%{name}-owner.patch
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
BuildRequires:	rpmbuild(macros) >= 1.202
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

%define		_sysconfdir	/etc/%{name}
%define		_apache1dir	/etc/apache
%define		_apache2dir	/etc/httpd

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

%description -l pl
MYSQLSTAT - zestaw narzêdzi do monitorowania, zapisywania i
wy¶wietlania statystyk systemu baz danych MySQL.

Rodzaje statystyk:
- Liczba zapytañ (zapytania/sekundê)
- Liczba po³±czeñ (po³±czenia/sekundê)
- Wej¶cie/wyj¶cie danych (bajty/sekundê)
- ¯±dania zapisu klucza (¿±dania/sekundê)
- ¯±dania odczytu klucza (¿±dania/sekundê)
- Zapisy klucza (zapisy/sekundê)
- Odczyty klucza (odczyty/sekundê)
- Rodzaje zapytañ
- Wykorzystanie tabel tymczasowych i na dysku

%package cgi
Summary:	MYSQLSTAT - CGI script
Summary(pl):	MYSQLSTAT - skrypt CGI
Group:		Applications/WWW
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	webserver = apache
Requires:	apache(mod_access)
Requires:	apache(mod_alias)
Requires:	apache(mod_cgi)

%description cgi
This package contains the cgi-script for MYSQLSTAT.

%description cgi -l pl
Ten pakiet zawiera skrypt CGI dla programu MYSQLSTAT.

%prep
%setup -q -n %{name}-%{version}-beta
%patch0 -p0
%patch1 -p0
%patch2 -p0

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
	HOME=$RPM_BUILD_ROOT%{_datadir}/%{name} \

install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/apache-%{name}.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%useradd -u %{userid} -d /usr/share/mysqlstat -s /bin/false -g http -c "MySQL Statistics" mysqlstat

%postun
if [ "$1" = "0" ]; then
	%userremove mysqlstat
fi

%preun cgi
if [ "$1" = "0" ]; then
	rm -f /var/lib/%{name}/cache/* 2>/dev/null || :
fi

%triggerin cgi -- apache1 >= 1.3.33-2
if [ "$1" = "1" ] && [ "$2" = "1" ] && [ -d %{_apache1dir}/conf.d ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf %{_apache1dir}/conf.d/99_%{name}.conf
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%triggerun cgi -- apache1 >= 1.3.33-2
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	if [ -L %{_apache1dir}/conf.d/99_%{name}.conf ]; then
		rm -f %{_apache1dir}/conf.d/99_%{name}.conf
		if [ -f /var/lock/subsys/apache ]; then
			/etc/rc.d/init.d/apache restart 1>&2
		fi
	fi
fi

%triggerin cgi -- apache >= 2.0.0
if [ "$1" = "1" ] && [ "$2" = "1" ] && [ -d %{_apache2dir}/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf %{_apache2dir}/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%triggerun cgi -- apache >= 2.0.0
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	if [ -L %{_apache2dir}/httpd.conf/99_%{name}.conf ]; then
		rm -f %{_apache2dir}/httpd.conf/99_%{name}.conf
		if [ -f /var/lock/subsys/httpd ]; then
			/etc/rc.d/init.d/httpd restart 1>&2
		fi
	fi
fi

# config path changed, trigger it
%triggerpostun cgi -- %{name}-cgi < 0.0.0.4-2.10
if [ -f /etc/httpd/mysqlstat.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/apache-%{name}.conf{,.rpmnew}
	mv -f /etc/httpd/mysqlstat.conf.rpmsave %{_sysconfdir}/apache-%{name}.conf
fi
if [ -d %{_apache2dir}/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf %{_apache2dir}/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc FAQ.RUS README.RUS TODO.RUS

%attr(700,mysqlstat,root) %dir %{_sysconfdir}
%attr(600,mysqlstat,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.conf

%dir %attr(750,mysqlstat,http) /var/lib/%{name}

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/mysqlstat.pm
%attr(755,root,root) %{_libdir}/%{name}/collector
%attr(755,root,root) %{_libdir}/%{name}/print_data

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}

%files cgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache-%{name}.conf
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%attr(755,root,root) %{_libdir}/%{name}/mysqlstat.cgi
%dir %attr(750,http,http) /var/lib/%{name}/cache
