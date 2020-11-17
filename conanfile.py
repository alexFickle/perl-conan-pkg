from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class PerlConanFile(ConanFile):
    name = "perl"
    version = "5.32.0"
    license = "GPLv1"
    settings = "os_build", "arch_build", "compiler"
    exports = "LICENSE"

    def _get_build_type(self):
        """
        Gets a string describing this build.
        Raises a ConanInvalidConfiguration if the settings are not supported.
        """
        if self.settings.compiler == "Visual Studio":
            return "MSVC" + tools.msvs_toolset(self)[1:]
        elif self.settings.os_build == "Linux":
            return "Linux"
        else:
            raise ConanInvalidConfiguration(
                "Unsupported compiler + os: {}, {}".format(
                    self.settings.compiler, self.settings.os_build))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        # ensures the platform is supported
        self._get_build_type()
    
    def build_requirements(self):
        if self._get_build_type() == "Linux":
            self.build_requires("make/4.2.1")

    def source(self):
        url = "https://www.cpan.org/src/5.0/perl-5.32.0.tar.gz"
        tar = "perl-5.32.0.tar.gz"
        tools.download(url, tar)
        tools.unzip(tar)
        os.remove(tar)

    def build(self):
        build_type = self._get_build_type()
        if build_type.startswith("MSVC"):
            command = \
                "{} && nmake CCTYPE={} INST_TOP={} /F Makefile install".format(
                    tools.vcvars_command(self),
                    build_type,
                    os.path.join(self.build_folder, "install")
                )
            self.run(command, cwd=os.path.join("perl-5.32.0", "win32"))
        elif build_type == "Linux":
            self.run(
                "./configure.gnu --prefix={}".format(
                    os.path.join(self.build_folder, "install")),
                cwd="perl-5.32.0"
            )
            self.run("make install", cwd="perl-5.32.0")
        else:
            # should not be reachable
            raise RuntimeError("Unhandled platform: {}".format(build_type))

    def package(self):
        self.copy("Copying", src="perl-5.32.0", dst="licenses")
        self.copy("*", src=os.path.join("install", "bin"), dst="bin")
        self.copy("*", src=os.path.join("install", "lib"), dst="lib")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "lib"))
