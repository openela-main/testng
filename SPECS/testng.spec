%bcond_without groovy
%bcond_without snakeyaml

Name:           testng
Version:        6.14.3
Release:        5%{?dist}
Summary:        Java-based testing framework
License:        ASL 2.0
URL:            http://testng.org/
# ./generate-tarball.sh
Source0:        %{name}-%{version}.tar.gz

# Allows building with maven instead of gradle
Source1:        pom.xml

# Remove bundled binaries to make sure we don't ship anything forbidden
Source2:        generate-tarball.sh

Patch0:         0001-Avoid-accidental-javascript-in-javadoc.patch
Patch1:         0002-Replace-bundled-jquery-with-CDN-link.patch

BuildArch:      noarch

BuildRequires:  maven-local
BuildRequires:  mvn(com.beust:jcommander)
BuildRequires:  mvn(com.google.inject:guice)
BuildRequires:  mvn(com.google.code.findbugs:jsr305)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.ant:ant)
BuildRequires:  mvn(org.apache-extras.beanshell:bsh)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.sonatype.oss:oss-parent:pom:)
%if %{with groovy}
BuildRequires:  mvn(org.assertj:assertj-core) >= 3.8.0
BuildRequires:  mvn(org.codehaus.gmavenplus:gmavenplus-plugin)
BuildRequires:  mvn(org.codehaus.groovy:groovy-all)
BuildRequires:  mvn(org.spockframework:spock-core)
%endif
%if %{with snakeyaml}
BuildRequires:  mvn(org.yaml:snakeyaml)
%endif

%description
TestNG is a testing framework inspired from JUnit and NUnit but introducing
some new functionality, including flexible test configuration, and
distributed test running.  It is designed to cover unit tests as well as
functional, end-to-end, integration, etc.

%package javadoc
Summary:        API documentation for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q

%patch0 -p1
%patch1 -p1

cp %{SOURCE1} .

# remove any bundled libs, but not test resources
find ! -path "*/test/*" -name *.jar -print -delete
find -name *.class -delete

# these are unnecessary
%pom_remove_plugin :maven-gpg-plugin
%pom_remove_plugin :maven-source-plugin
%pom_remove_plugin :maven-javadoc-plugin

%if %{without snakeyaml}
%pom_remove_dep org.yaml:snakeyaml
rm src/main/java/org/testng/internal/Yaml*.java
rm src/main/java/org/testng/Converter.java
%endif

# missing test deps
%if %{with groovy}
%pom_add_plugin "org.codehaus.gmavenplus:gmavenplus-plugin" pom.xml \
  "<executions><execution><goals><goal>addTestSources</goal><goal>testGenerateStubs</goal><goal>testCompile</goal><goal>removeTestStubs</goal></goals></execution></executions>"
%pom_add_dep "org.assertj:assertj-core::test"
%pom_add_dep "org.spockframework:spock-core::test"
%pom_add_dep "org.codehaus.groovy:groovy-all::test"

# remove failing test
sed -i -e '/parallelDataProviderSample/,+12d' ./src/test/java/test/dataprovider/DataProviderTest.java
%endif

sed -i -e 's/DEV-SNAPSHOT/%{version}/' src/main/java/org/testng/internal/Version.java

cp -p ./src/main/java/*.dtd.html ./src/main/resources/.

%mvn_file : %{name}
# jdk15 classifier is used by some other packages
%mvn_alias : :::jdk15:

%build
%if %{with groovy} && %{with snakeyaml}
%mvn_build
%else
%mvn_build -f
%endif

%install
%mvn_install

%files -f .mfiles
%doc CHANGES.txt README.md
%license LICENSE.txt

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
* Wed Jul 18 2018 Michael Simacek <msimacek@redhat.com> - 6.14.3-5
- Clean tarball from binaries
- Replace bundled jquery with CDN link

* Tue Jul 17 2018 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.14.3-4
- Allow conditionally building without snakeyaml

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.14.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Mar 20 2018 Alexander Kurtakov <akurtako@redhat.com> 6.14.3-2
- Bump maven pom version.

* Tue Mar 20 2018 Alexander Kurtakov <akurtako@redhat.com> 6.14.3-1
- Update to upstream 6.14.3.

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 23 2017 Mat Booth <mat.booth@redhat.com> - 6.12-2
- Allow OSGi metadata to export all packages including internal ones

* Fri Jul 28 2017 Mat Booth <mat.booth@redhat.com> - 6.12-1
- Update to latest release of testng
- Fixes classloading from ant rhbz#1475842

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 6.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 04 2017 Mat Booth <mat.booth@redhat.com> - 6.11-1
- Update to latest upstream release
- Continue building with maven for now, instead of moving to gradle due to
  rhbz#1467724

* Wed May 31 2017 Michael Simacek <msimacek@redhat.com> - 6.9.12-5
- Avoid accidental javascript in comment

* Fri Feb 17 2017 Mat Booth <mat.booth@redhat.com> - 6.9.12-4
- License correction

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 6.9.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb  1 2017 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.9.12-2
- Introduce build-conditional to allow building without groovy

* Tue Nov 01 2016 Mat Booth <mat.booth@redhat.com> - 6.9.12-1
- Update to upstream version 6.9.12
- Avoid 'SNAPSHOT' in pom version to fix tests in testng-remote package

* Wed Apr 20 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.9.11-1
- Update to upstream version 6.9.11

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 6.9.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 08 2016 gil cattaneo <puntogil@libero.it> 6.9.10-1
- Update to 6.9.10

* Tue Oct 27 2015 gil cattaneo <puntogil@libero.it> 6.9.9-1
- Update to 6.9.9

* Tue Oct 13 2015 gil cattaneo <puntogil@libero.it> 6.9.8-1
- Update to 6.9.8

* Mon Sep 07 2015 Mat Booth <mat.booth@redhat.com> - 6.9.5-1
- Update to 6.9.5

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.8.21-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jan 20 2015 gil cattaneo <puntogil@libero.it> 6.8.21-1
- Update to 6.8.21
- introduce license macro

* Tue Jan 20 2015 gil cattaneo <puntogil@libero.it> 6.8.17-1
- Update to 6.8.17

* Wed Jan 14 2015 gil cattaneo <puntogil@libero.it> 6.8.14-1
- Update to 6.8.14

* Mon Aug  4 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.8.8-3
- Fix build-requires on sonatype-oss-parent

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.8.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Feb 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.8.8-1
- Update to upstream version 6.8.8

* Thu Sep 12 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 6.8.7-1
- Update to upstream version 6.8.7
- Provide additional jdk15 classifier

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.8.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue May 14 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.8.5-1
- Update to upstream version 6.8.5

* Sun Feb 10 2013 Mat Booth <fedora@matbooth.co.uk> - 6.8-1
- Update to latest upstream release, rhbz #888233

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 6.0.1-6
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Thu Nov 08 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 6.0.1-5
- Part of testng is CPL, add it to license tag

* Thu Jul 26 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 6.0.1-4
- Spec file cleanups and add_maven_depmap macro use
- Drop no longer needed depmap

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu May 12 2011 Jaromir Capik <jcapik@redhat.com> - 6.0.1-1
- Update to 6.0.1

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jul 19 2010 Lubomir Rintel <lkundrak@v3.sk> - 5.11-3
- Drop backport util concurrent dependency, we don't build jdk14 jar

* Mon Dec 21 2009 Lubomir Rintel <lkundrak@v3.sk> - 5.11-2
- Add POM

* Sun Dec 20 2009 Lubomir Rintel <lkundrak@v3.sk> - 5.11-1
- Bump to 5.11
- Add maven depmap fragments
- Fix line encoding of README

* Wed Dec 09 2009 Lubomir Rintel <lkundrak@v3.sk> - 5.10-2
- Add javadoc
- Don't ship jdk14 jar

* Fri Nov 27 2009 Lubomir Rintel <lkundrak@v3.sk> - 5.10-1
- Initial packaging
