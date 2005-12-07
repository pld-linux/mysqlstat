%include	/usr/lib/rpm/macros.perl
Summary:	MYSQLSTAT - utilities to monitor, store and display MySQL DBMS usage statistics
Summary(pl):	MYSQLSTAT - narzêdzia do monitorowania, zapisywania i wy¶wietlania statystyk MySQL
Name:		mysqlstat
Version:	0.0.0.4
Release:	5.7
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
Patch3:		%{name}-qcache.patch
Patch4:		%{name}-emptypass.patch
Patch5:		%{name}-ndebug.patch
URL:		http://www.mysqlstat.org/en/
BuildRequires:	perl-AppConfig >= 1.52
BuildRequires:	perl-CGI >= 2.752
BuildRequires:	perl-DBI >= 1.19
BuildRequires:	perl-Digest-MD5 >= 1.19
BuildRequires:	perl(Fcntl) >= 1.03
BuildRequires:	perl-HTML-Template >= 2.5
BuildRequires:	perl-DBD-mysql >= 1.221
BuildRequires:	perl-Storable >= 2.04
BuildRequires:	perl-rrdtool >= 1.00
BuildRequires:	rpmbuild(macros) >= 1.264
Requires:	crondaemon
Requires:	perl-AppConfig >= 1.52
Requires:	perl-DBI >= 1.19
Requires:	perl(Fcntl) >= 1.03
Requires:	perl-DBD-mysql >= 1.221
Requires:	perl-Storable >= 2.04
Requires:	perl-rrdtool >= 1.00
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
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
Requires:	webapps
Requires:	apache(mod_access)
Requires:	apache(mod_alias)
Requires:	apache(mod_auth)
Requires:	apache(mod_cgi)
Requires:	perl-CGI >= 2.752
Requires:	perl-Digest-MD5 >= 1.19
Requires:	perl-HTML-Template >= 2.5

%description cgi
This package contains the cgi-script for MYSQLSTAT.

%description cgi -l pl
Ten pakiet zawiera skrypt CGI dla programu MYSQLSTAT.

%prep
%setup -q -n %{name}-%{version}-beta
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p1
%patch4 -p1
%patch5 -p1

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
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

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

%triggerin -- apache1
%webapp_register apache %{_webapp}

%triggerun -- apache1
%webapp_unregister apache %{_webapp}

%triggerin -- apache >= 2.0.0
%webapp_register httpd %{_webapp}

%triggerun -- apache >= 2.0.0
%webapp_unregister httpd %{_webapp}

%triggerpostun cgi -- mysqlstat-cgi < 0.0.0.4-2.10
# config path changed, trigger it
if [ -f /etc/httpd/mysqlstat.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/apache-%{name}.conf{,.rpmnew}
	mv -f /etc/httpd/mysqlstat.conf.rpmsave %{_sysconfdir}/apache-%{name}.conf
fi
if [ -d /etc/httpd/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd reload 1>&2
	fi
fi

%triggerpostun -- %{name} < 0.0.0.4-2.14
echo >&2 "IMPORTANT: Renaming .rrd files to .old as the file format has changed!"
for a in /var/lib/%{name}/*.rrd; do
	mv -v $a $a.old
done

%triggerpostun cgi -- mysqlstat-cgi < 0.0.0.4-5.1
# migrate from apache-config macros
if [ -f /etc/mysqlstat/apache-mysqlstat.conf.rpmsave ]; then
	if [ -d /etc/apache/webapps.d ]; then
		cp -f %{_sysconfdir}/apache.conf{,.rpmnew}
		cp -f /etc/mysqlstat/apache-mysqlstat.conf.rpmsave %{_sysconfdir}/apache.conf
	fi

	if [ -d /etc/httpd/webapps.d ]; then
		cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
		cp -f /etc/mysqlstat/apache-mysqlstat.conf.rpmsave %{_sysconfdir}/httpd.conf
	fi
	rm -f /etc/mysqlstat/apache-mysqlstat.conf.rpmsave
fi

# place new config location, as trigger puts config only on first install, do it here.
if [ -d /etc/apache/webapps.d ]; then
	/usr/sbin/webapp register apache %{_webapp}
	apache_reload=1
fi
if [ -d /etc/httpd/webapps.d ]; then
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

# register webapp on apaches which were registered earlier
if [ -L /etc/apache/conf.d/99_mysqlstat.conf ]; then
	rm -f /etc/apache/conf.d/99_mysqlstat.conf
	/usr/sbin/webapp register apache %{_webapp}
	apache_reload=1
fi
if [ -L /etc/httpd/httpd.conf/99_mysqlstat.conf ]; then
	rm -f /etc/httpd/httpd.conf/99_mysqlstat.conf
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

if [ "$httpd_reload" ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd reload 1>&2
	fi
fi
if [ "$apache_reload" ]; then
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache reload 1>&2
	fi
fi

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
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%attr(755,root,root) %{_prefix}/lib/%{name}/mysqlstat.cgi
%dir %attr(750,http,http) /var/cache/%{name}
