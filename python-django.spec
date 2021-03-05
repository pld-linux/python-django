# NOTE: for versions >= 2.0 (for python 3.5+) see python3-django.spec
#
# Conditional build:
%bcond_without	doc	# Sphinx documentation
%bcond_without	python2 # CPython 2.x module
%bcond_with	python3 # CPython 3.x module (built from python3-django.spec)
%bcond_with	tests	# unit tests [failing: 1E, 1F as of 1.11.29]

%define		module		django
%define		egg_name	Django
Summary:	The web framework for perfectionists with deadlines
Summary(pl.UTF-8):	Szkielet WWW dla perfekcjonistów z ograniczeniami czasowymi
Name:		python-%{module}
# keep 1.11.x here for python2 support
Version:	1.11.29
Release:	3
License:	BSD
Group:		Libraries/Python
Source0:	https://www.djangoproject.com/m/releases/1.11/Django-%{version}.tar.gz
# Source0-md5:	e725953dfc63ea9e3b5b0898a8027bd7
Patch0:		%{name}-sphinx.patch
URL:		https://www.djangoproject.com/
%if %(locale -a | grep -q '^C\.utf8$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(find_lang) >= 1.40
BuildRequires:	rpmbuild(macros) >= 1.714
%{?with_doc:BuildRequires:	sphinx-pdg}
%if %{with python2}
BuildRequires:	python-devel >= 1:2.7
BuildRequires:	python-setuptools
%if %{with tests}
BuildRequires:	python-pytz
%endif
%endif
%if %{with python3}
BuildRequires:	python3-devel >= 1:3.4
BuildRequires:	python3-setuptools
%if %{with tests}
BuildRequires:	python3-pytz
%endif
%endif
%if %{with doc}
BuildRequires:	sphinx-pdg >= 1.8
%endif
Suggests:	python-MySQLdb
Suggests:	python-PyGreSQL
Suggests:	python-devel-tools
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Django is a high-level Python Web framework that encourages rapid
development and clean, pragmatic design.

%description -l pl.UTF-8
Django to wysokopoziomowy szkielet dla serwisów WWW w Pythonie
wspierający szybkie tworzenie i czysty, pragmatyczny projekt.

%package -n python3-%{module}
Summary:	The web framework for perfectionists with deadlines
Summary(pl.UTF-8):	Szkielet WWW dla perfekcjonistów z ograniczeniami czasowymi
Group:		Libraries/Python
Suggests:	python3-MySQLdb
Suggests:	python3-devel-tools
Suggests:	python3-psycopg2
Conflicts:	python-django < 1.11.29

%description -n python3-%{module}
Django is a high-level Python Web framework that encourages rapid
development and clean, pragmatic design.

%description -n python3-%{module} -l pl.UTF-8
Django to wysokopoziomowy szkielet dla serwisów WWW w Pythonie
wspierający szybkie tworzenie i czysty, pragmatyczny projekt.

%package doc
Summary:	Documentation on Django
Summary(de.UTF-8):	Dokumentation zu Django
Summary(es.UTF-8):	Documentación para Django
Summary(fr.UTF-8):	Documentation sur Django
Summary(pl.UTF-8):	Dokumentacja do Django
Group:		Documentation

%description doc
Documentation on Django.

%description doc -l pl.UTF-8
Dokumentacja do Django.

%prep
%setup -q -n Django-%{version}
%patch0 -p1

%build
%if %{with python2}
%py_build

%if %{with tests}
LC_ALL=C.UTF-8 \
PYTHONPATH=$(pwd)/build-2/lib \
%{__python} tests/runtests.py --parallel 1
%endif
%endif

%if %{with python3}
%py3_build

%if %{with tests}
LC_ALL=C.UTF-8 \
PYTHONPATH=$(pwd)/build-3/lib \
%{__python3} tests/runtests.py --parallel 1
%endif
%endif

%if %{with doc}
%{__make} -C docs html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with python2}
%py_install
%py_postclean

%{__mv} $RPM_BUILD_ROOT%{_bindir}/{django-admin.py,django-admin-2}
ln -s django-admin-2 $RPM_BUILD_ROOT%{_bindir}/py2-django-admin

%{__sed} -i -e '1s,/usr/bin/env python$,%{__python},' $RPM_BUILD_ROOT%{py_sitescriptdir}/django/conf/project_template/manage.py-tpl
%endif

%if %{with python3}
%py3_install

%{__mv} $RPM_BUILD_ROOT%{_bindir}/{django-admin.py,django-admin-3}
ln -s django-admin-3 $RPM_BUILD_ROOT%{_bindir}/py3-django-admin

%{__sed} -i -e '1s,/usr/bin/env python$,%{__python3},' $RPM_BUILD_ROOT%{py3_sitescriptdir}/django/conf/project_template/manage.py-tpl
%{__sed} -i -e '1s,/usr/bin/env python$,%{__python3},' $RPM_BUILD_ROOT%{py3_sitescriptdir}/django/bin/django-admin.py
%endif

# setup "django-admin" global alias
%if %{with python3}
ln -sf py3-django-admin $RPM_BUILD_ROOT%{_bindir}/django-admin
%endif

%if %{with doc}
install -d $RPM_BUILD_ROOT%{_docdir}
ln -sf python-django-doc-%{version} $RPM_BUILD_ROOT%{_docdir}/python-django-doc
%endif

# don't package .po sources
find \
	%{?with_python2:$RPM_BUILD_ROOT%{py_sitescriptdir}/%{module}} \
	%{?with_python3:$RPM_BUILD_ROOT%{py3_sitescriptdir}/%{module}} \
	-name django.po -o \
	-name djangojs.po | xargs %{__rm} -v

%find_lang django --with-django --all-name

# fix after find-lang:
# - remove __pycache__ "language"
# - drop charsets from lang names (django uses non-standard _Charset instead of @charset)
grep -v __pycache__ <django.lang | \
	sed -e 's/lang(sr_Latn)/lang(sr)/;s/lang(zh_Hans)/lang(zh_CN)/;s/lang(zh_Hant)/lang(zh_TW)/' > django_fixed.lang

# separate lang to Python 2 and Python 3 files
%if %{with python2}
grep python2 django_fixed.lang > python2-django.lang
%endif
%if %{with python3}
grep python3 django_fixed.lang > python3-django.lang
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with python2}
%files -f python2-django.lang
%defattr(644,root,root,755)
%doc AUTHORS LICENSE README.rst
%attr(755,root,root) %{_bindir}/django-admin-2
%attr(755,root,root) %{_bindir}/py2-django-admin
%dir %{py_sitescriptdir}/%{module}
%{py_sitescriptdir}/%{module}/*.py[co]
%{py_sitescriptdir}/%{module}/apps
%{py_sitescriptdir}/%{module}/bin
%{py_sitescriptdir}/%{module}/core
%{py_sitescriptdir}/%{module}/db
%{py_sitescriptdir}/%{module}/dispatch
%{py_sitescriptdir}/%{module}/forms
%{py_sitescriptdir}/%{module}/http
%{py_sitescriptdir}/%{module}/middleware
%{py_sitescriptdir}/%{module}/template
%{py_sitescriptdir}/%{module}/templatetags
%{py_sitescriptdir}/%{module}/test
%{py_sitescriptdir}/%{module}/urls
%{py_sitescriptdir}/%{module}/utils
%{py_sitescriptdir}/%{module}/views

%dir %{py_sitescriptdir}/%{module}/conf
%{py_sitescriptdir}/%{module}/conf/*.py[co]
%{py_sitescriptdir}/%{module}/conf/app_template
%dir %{py_sitescriptdir}/%{module}/conf/locale
%{py_sitescriptdir}/%{module}/conf/locale/__init__.py[co]
%{py_sitescriptdir}/%{module}/conf/project_template
%{py_sitescriptdir}/%{module}/conf/urls

%dir %{py_sitescriptdir}/%{module}/contrib
%{py_sitescriptdir}/%{module}/contrib/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/admin
%{py_sitescriptdir}/%{module}/contrib/admin/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/admin/locale
%{py_sitescriptdir}/%{module}/contrib/admin/migrations
%{py_sitescriptdir}/%{module}/contrib/admin/static
%{py_sitescriptdir}/%{module}/contrib/admin/templates
%{py_sitescriptdir}/%{module}/contrib/admin/templatetags
%{py_sitescriptdir}/%{module}/contrib/admin/views
%dir %{py_sitescriptdir}/%{module}/contrib/admindocs
%{py_sitescriptdir}/%{module}/contrib/admindocs/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/admindocs/locale
%{py_sitescriptdir}/%{module}/contrib/admindocs/templates
%dir %{py_sitescriptdir}/%{module}/contrib/auth
%{py_sitescriptdir}/%{module}/contrib/auth/*.py[co]
%{py_sitescriptdir}/%{module}/contrib/auth/common-passwords.txt.gz
%{py_sitescriptdir}/%{module}/contrib/auth/handlers
%dir %{py_sitescriptdir}/%{module}/contrib/auth/locale
%{py_sitescriptdir}/%{module}/contrib/auth/management
%{py_sitescriptdir}/%{module}/contrib/auth/migrations
%{py_sitescriptdir}/%{module}/contrib/auth/templates
%{py_sitescriptdir}/%{module}/contrib/auth/tests
%dir %{py_sitescriptdir}/%{module}/contrib/contenttypes
%{py_sitescriptdir}/%{module}/contrib/contenttypes/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/contenttypes/locale
%{py_sitescriptdir}/%{module}/contrib/contenttypes/management
%{py_sitescriptdir}/%{module}/contrib/contenttypes/migrations
%dir %{py_sitescriptdir}/%{module}/contrib/flatpages
%{py_sitescriptdir}/%{module}/contrib/flatpages/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/flatpages/locale
%{py_sitescriptdir}/%{module}/contrib/flatpages/migrations
%{py_sitescriptdir}/%{module}/contrib/flatpages/templatetags
%dir %{py_sitescriptdir}/%{module}/contrib/gis
%{py_sitescriptdir}/%{module}/contrib/gis/*.py[co]
%{py_sitescriptdir}/%{module}/contrib/gis/admin
%{py_sitescriptdir}/%{module}/contrib/gis/db
%{py_sitescriptdir}/%{module}/contrib/gis/forms
%{py_sitescriptdir}/%{module}/contrib/gis/gdal
%{py_sitescriptdir}/%{module}/contrib/gis/geoip
%{py_sitescriptdir}/%{module}/contrib/gis/geoip2
%{py_sitescriptdir}/%{module}/contrib/gis/geometry
%{py_sitescriptdir}/%{module}/contrib/gis/geos
%dir %{py_sitescriptdir}/%{module}/contrib/gis/locale
%{py_sitescriptdir}/%{module}/contrib/gis/management
%{py_sitescriptdir}/%{module}/contrib/gis/serializers
%{py_sitescriptdir}/%{module}/contrib/gis/sitemaps
%{py_sitescriptdir}/%{module}/contrib/gis/static
%{py_sitescriptdir}/%{module}/contrib/gis/templates
%{py_sitescriptdir}/%{module}/contrib/gis/utils
%dir %{py_sitescriptdir}/%{module}/contrib/humanize
%{py_sitescriptdir}/%{module}/contrib/humanize/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/humanize/locale
%{py_sitescriptdir}/%{module}/contrib/humanize/templatetags
%dir %{py_sitescriptdir}/%{module}/contrib/messages
%{py_sitescriptdir}/%{module}/contrib/messages/*.py[co]
%{py_sitescriptdir}/%{module}/contrib/messages/storage
%dir %{py_sitescriptdir}/%{module}/contrib/postgres
%{py_sitescriptdir}/%{module}/contrib/postgres/*.py[co]
%{py_sitescriptdir}/%{module}/contrib/postgres/aggregates
%{py_sitescriptdir}/%{module}/contrib/postgres/fields
%{py_sitescriptdir}/%{module}/contrib/postgres/forms
%{py_sitescriptdir}/%{module}/contrib/postgres/jinja2
%dir %{py_sitescriptdir}/%{module}/contrib/postgres/locale
%{py_sitescriptdir}/%{module}/contrib/postgres/templates
%dir %{py_sitescriptdir}/%{module}/contrib/redirects
%{py_sitescriptdir}/%{module}/contrib/redirects/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/redirects/locale
%{py_sitescriptdir}/%{module}/contrib/redirects/migrations
%dir %{py_sitescriptdir}/%{module}/contrib/sessions
%{py_sitescriptdir}/%{module}/contrib/sessions/*.py[co]
%{py_sitescriptdir}/%{module}/contrib/sessions/backends
%dir %{py_sitescriptdir}/%{module}/contrib/sessions/locale
%{py_sitescriptdir}/%{module}/contrib/sessions/management
%{py_sitescriptdir}/%{module}/contrib/sessions/migrations
%{py_sitescriptdir}/%{module}/contrib/sitemaps
%dir %{py_sitescriptdir}/%{module}/contrib/sites
%{py_sitescriptdir}/%{module}/contrib/sites/*.py[co]
%dir %{py_sitescriptdir}/%{module}/contrib/sites/locale
%{py_sitescriptdir}/%{module}/contrib/sites/migrations
%{py_sitescriptdir}/%{module}/contrib/staticfiles
%{py_sitescriptdir}/%{module}/contrib/syndication
%{py_sitescriptdir}/%{egg_name}-%{version}-py*.egg-info
%endif

%if %{with python3}
%files -n python3-%{module} -f python3-django.lang
%defattr(644,root,root,755)
%doc AUTHORS LICENSE README.rst
%attr(755,root,root) %{_bindir}/django-admin
%attr(755,root,root) %{_bindir}/django-admin-3
%attr(755,root,root) %{_bindir}/py3-django-admin
%dir %{py3_sitescriptdir}/%{module}
%{py3_sitescriptdir}/%{module}/*.py
%{py3_sitescriptdir}/%{module}/__pycache__
%{py3_sitescriptdir}/%{module}/apps
%{py3_sitescriptdir}/%{module}/bin
%{py3_sitescriptdir}/%{module}/core
%{py3_sitescriptdir}/%{module}/db
%{py3_sitescriptdir}/%{module}/dispatch
%{py3_sitescriptdir}/%{module}/forms
%{py3_sitescriptdir}/%{module}/http
%{py3_sitescriptdir}/%{module}/middleware
%{py3_sitescriptdir}/%{module}/template
%{py3_sitescriptdir}/%{module}/templatetags
%{py3_sitescriptdir}/%{module}/test
%{py3_sitescriptdir}/%{module}/urls
%{py3_sitescriptdir}/%{module}/utils
%{py3_sitescriptdir}/%{module}/views

%dir %{py3_sitescriptdir}/%{module}/conf
%{py3_sitescriptdir}/%{module}/conf/*.py
%{py3_sitescriptdir}/%{module}/conf/__pycache__
%{py3_sitescriptdir}/%{module}/conf/app_template
%dir %{py3_sitescriptdir}/%{module}/conf/locale
%{py3_sitescriptdir}/%{module}/conf/locale/__init__.py
%{py3_sitescriptdir}/%{module}/conf/locale/__pycache__
%{py3_sitescriptdir}/%{module}/conf/project_template
%{py3_sitescriptdir}/%{module}/conf/urls

%dir %{py3_sitescriptdir}/%{module}/contrib
%{py3_sitescriptdir}/%{module}/contrib/*.py
%{py3_sitescriptdir}/%{module}/contrib/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/admin
%{py3_sitescriptdir}/%{module}/contrib/admin/*.py
%{py3_sitescriptdir}/%{module}/contrib/admin/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/admin/locale
%{py3_sitescriptdir}/%{module}/contrib/admin/migrations
%{py3_sitescriptdir}/%{module}/contrib/admin/static
%{py3_sitescriptdir}/%{module}/contrib/admin/templates
%{py3_sitescriptdir}/%{module}/contrib/admin/templatetags
%{py3_sitescriptdir}/%{module}/contrib/admin/views
%dir %{py3_sitescriptdir}/%{module}/contrib/admindocs
%{py3_sitescriptdir}/%{module}/contrib/admindocs/*.py
%{py3_sitescriptdir}/%{module}/contrib/admindocs/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/admindocs/locale
%{py3_sitescriptdir}/%{module}/contrib/admindocs/templates
%dir %{py3_sitescriptdir}/%{module}/contrib/auth
%{py3_sitescriptdir}/%{module}/contrib/auth/*.py
%{py3_sitescriptdir}/%{module}/contrib/auth/__pycache__
%{py3_sitescriptdir}/%{module}/contrib/auth/common-passwords.txt.gz
%{py3_sitescriptdir}/%{module}/contrib/auth/handlers
%dir %{py3_sitescriptdir}/%{module}/contrib/auth/locale
%{py3_sitescriptdir}/%{module}/contrib/auth/management
%{py3_sitescriptdir}/%{module}/contrib/auth/migrations
%{py3_sitescriptdir}/%{module}/contrib/auth/templates
%{py3_sitescriptdir}/%{module}/contrib/auth/tests
%dir %{py3_sitescriptdir}/%{module}/contrib/contenttypes
%{py3_sitescriptdir}/%{module}/contrib/contenttypes/*.py
%{py3_sitescriptdir}/%{module}/contrib/contenttypes/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/contenttypes/locale
%{py3_sitescriptdir}/%{module}/contrib/contenttypes/management
%{py3_sitescriptdir}/%{module}/contrib/contenttypes/migrations
%dir %{py3_sitescriptdir}/%{module}/contrib/flatpages
%{py3_sitescriptdir}/%{module}/contrib/flatpages/*.py
%{py3_sitescriptdir}/%{module}/contrib/flatpages/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/flatpages/locale
%{py3_sitescriptdir}/%{module}/contrib/flatpages/migrations
%{py3_sitescriptdir}/%{module}/contrib/flatpages/templatetags
%dir %{py3_sitescriptdir}/%{module}/contrib/gis
%{py3_sitescriptdir}/%{module}/contrib/gis/*.py
%{py3_sitescriptdir}/%{module}/contrib/gis/__pycache__
%{py3_sitescriptdir}/%{module}/contrib/gis/admin
%{py3_sitescriptdir}/%{module}/contrib/gis/db
%{py3_sitescriptdir}/%{module}/contrib/gis/forms
%{py3_sitescriptdir}/%{module}/contrib/gis/gdal
%{py3_sitescriptdir}/%{module}/contrib/gis/geoip
%{py3_sitescriptdir}/%{module}/contrib/gis/geoip2
%{py3_sitescriptdir}/%{module}/contrib/gis/geometry
%{py3_sitescriptdir}/%{module}/contrib/gis/geos
%dir %{py3_sitescriptdir}/%{module}/contrib/gis/locale
%{py3_sitescriptdir}/%{module}/contrib/gis/management
%{py3_sitescriptdir}/%{module}/contrib/gis/serializers
%{py3_sitescriptdir}/%{module}/contrib/gis/sitemaps
%{py3_sitescriptdir}/%{module}/contrib/gis/static
%{py3_sitescriptdir}/%{module}/contrib/gis/templates
%{py3_sitescriptdir}/%{module}/contrib/gis/utils
%dir %{py3_sitescriptdir}/%{module}/contrib/humanize
%{py3_sitescriptdir}/%{module}/contrib/humanize/*.py
%{py3_sitescriptdir}/%{module}/contrib/humanize/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/humanize/locale
%{py3_sitescriptdir}/%{module}/contrib/humanize/templatetags
%dir %{py3_sitescriptdir}/%{module}/contrib/messages
%{py3_sitescriptdir}/%{module}/contrib/messages/*.py
%{py3_sitescriptdir}/%{module}/contrib/messages/__pycache__
%{py3_sitescriptdir}/%{module}/contrib/messages/storage
%dir %{py3_sitescriptdir}/%{module}/contrib/postgres
%{py3_sitescriptdir}/%{module}/contrib/postgres/*.py
%{py3_sitescriptdir}/%{module}/contrib/postgres/__pycache__
%{py3_sitescriptdir}/%{module}/contrib/postgres/aggregates
%{py3_sitescriptdir}/%{module}/contrib/postgres/fields
%{py3_sitescriptdir}/%{module}/contrib/postgres/forms
%{py3_sitescriptdir}/%{module}/contrib/postgres/jinja2
%dir %{py3_sitescriptdir}/%{module}/contrib/postgres/locale
%{py3_sitescriptdir}/%{module}/contrib/postgres/templates
%dir %{py3_sitescriptdir}/%{module}/contrib/redirects
%{py3_sitescriptdir}/%{module}/contrib/redirects/*.py
%{py3_sitescriptdir}/%{module}/contrib/redirects/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/redirects/locale
%{py3_sitescriptdir}/%{module}/contrib/redirects/migrations
%dir %{py3_sitescriptdir}/%{module}/contrib/sessions
%{py3_sitescriptdir}/%{module}/contrib/sessions/*.py
%{py3_sitescriptdir}/%{module}/contrib/sessions/__pycache__
%{py3_sitescriptdir}/%{module}/contrib/sessions/backends
%dir %{py3_sitescriptdir}/%{module}/contrib/sessions/locale
%{py3_sitescriptdir}/%{module}/contrib/sessions/management
%{py3_sitescriptdir}/%{module}/contrib/sessions/migrations
%{py3_sitescriptdir}/%{module}/contrib/sitemaps
%dir %{py3_sitescriptdir}/%{module}/contrib/sites
%{py3_sitescriptdir}/%{module}/contrib/sites/*.py
%{py3_sitescriptdir}/%{module}/contrib/sites/__pycache__
%dir %{py3_sitescriptdir}/%{module}/contrib/sites/locale
%{py3_sitescriptdir}/%{module}/contrib/sites/migrations
%{py3_sitescriptdir}/%{module}/contrib/staticfiles
%{py3_sitescriptdir}/%{module}/contrib/syndication

%{py3_sitescriptdir}/%{egg_name}-%{version}-py*.egg-info
%endif

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc docs/_build/html/{_downloads,_images,_modules,_static,faq,howto,internals,intro,misc,ref,releases,topics,*.html,*.js}
%{_docdir}/python-django-doc
%endif
