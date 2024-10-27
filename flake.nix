
{
  description = "Command line utility to control wiz ligths";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        python = pkgs.python312;
        wiz-cli = python.pkgs.callPackage ./package.nix {}; 
      in {
        packages = { inherit wiz-cli; };
        defaultPackage = wiz-cli;
        overlays = [
          (final: prev: {
            inherit wiz-cli;
          })
        ];
        devShells.default = pkgs.mkShell {
          buildInputs = [ 
            wiz-cli
          ];
          shellHook = ''
            export FLAKE="wiz-cli"
            # back to zsh
            exec zsh
          '';
        };
      }
    );
}
