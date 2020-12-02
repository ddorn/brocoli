{
  # name = "brocoli"
  description = "Mandelbrot set explorer and generator written in python and kivy.";

  inputs = {
    # https://github.com/NixOS/nixpkgs/pull/104694
    nixpkgs.url = "github:rissson/nixpkgs/kivy-2.0";
    futils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, futils, flake-compat }:
    let
      inherit (nixpkgs) lib;
      inherit (futils.lib) eachDefaultSystem defaultSystems;
      inherit (lib) recursiveUpdate;

      nixpkgsFor = lib.genAttrs defaultSystems (system: import nixpkgs {
        inherit system;
        overlays = [ self.overlay ];
      });

      ddorn = {
        email = "diego.dorn@free.fr";
        name = "Diego Dorn";
        github = "ddorn";
        githubId = 27305483;
      };

      poetryArgs = pkgs: {
        projectDir = self;
        src = self;

        overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
          # Force fetching from nixpkgs
          kivy = pkgs.python3Packages.kivy;
          kivymd = pkgs.kivymd;
          numba = pkgs.python3Packages.numba;
          tweepy = pkgs.python3Packages.tweepy;

          colour = super.colour.overridePythonAttrs (old: {
            buildInputs = old.buildInputs ++ [ self.d2to1 ];
          });
        });

        meta = with lib; {
          inherit (self) description;
          maintainers = [ ddorn ];
          license = licenses.mit;
        };
      };
    in
    recursiveUpdate
    {
      overlay = final: prev: {
        kivymd = final.python3Packages.buildPythonPackage rec {
          pname = "kivymd";
          version = "0.104.1";

          src = final.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "19nnr2r2v22k1jqf982lfbaws5686bdzv611ay19rppzib5w5jwx";
          };

          buildInputs = with final; [
            python3Packages.kivy
            python3Packages.kivy-garden
            python3Packages.pygments
            python3Packages.requests
          ];

          doCheck = false;

          meta = with lib; {
            description = "Set of widgets for Kivy inspired by Google's Material Design";
            maintainers = [ ddorn ];
            license = licenses.mit;
          };
        };

        brocoli = final.poetry2nix.mkPoetryApplication (poetryArgs final);

        brocoli-docker = final.dockerTools.buildLayeredImage {
          name = "brocoli";
          config = {
            Cmd = [ "${final.brocoli}/bin/brocoli" ];
            Entrypoint = "${final.brocoli}/bin/brocoli";
          };
        };
      };
    }
    (eachDefaultSystem (system:
      let
        pkgs = nixpkgsFor.${system};
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            (pkgs.poetry2nix.mkPoetryEnv (removeAttrs (poetryArgs pkgs) [ "meta" "src" ]))
          ];

          PYTHONPATH = ".";
        };

        packages = {
          inherit (pkgs) brocoli brocoli-docker kivymd;
        };
        defaultPackage = self.packages.${system}.brocoli;
      }
    ));
}
