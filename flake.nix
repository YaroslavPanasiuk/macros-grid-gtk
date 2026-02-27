{
  description = "Python GTK4 Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python3;
    in {
      packages.${system}.default = python.pkgs.buildPythonApplication {
        pname = "macro-grid";
        version = "1.0.0";
        format = "other";

        src = ./.;

        nativeBuildInputs = [
          pkgs.gobject-introspection
          pkgs.wrapGAppsHook4
          pkgs.copyDesktopItems
        ];

        propagatedBuildInputs = [
          python.pkgs.pygobject3
          pkgs.gtk4
          pkgs.adwaita-icon-theme
        ];

        desktopItems = [
          (pkgs.makeDesktopItem {
            name = "macro-grid";
            exec = "macro-grid";
            icon = "macro-grid";
            desktopName = "Macro Grid";
            comment = "GTK Command Launcher";
            categories = [ "Utility" "System" ];
            terminal = false;
          })
        ];

        installPhase = ''
          mkdir -p $out/bin
          cp main.py $out/bin/macro-grid
          cp style.css $out/bin/style.css
          cp layout.ui $out/bin/layout.ui
          cp settings.json $out/bin/settings.json
          chmod +x $out/bin/macro-grid
          mkdir -p $out/share/icons/hicolor/16x16/apps
          cp ${./icons/16x16.png} $out/share/icons/hicolor/16x16/apps/macro-grid.png

          mkdir -p $out/share/icons/hicolor/32x32/apps
          cp ${./icons/32x32.png} $out/share/icons/hicolor/32x32/apps/macro-grid.png

          mkdir -p $out/share/icons/hicolor/64x64/apps
          cp ${./icons/64x64.png} $out/share/icons/hicolor/64x64/apps/macro-grid.png

          mkdir -p $out/share/icons/hicolor/128x128/apps
          cp ${./icons/128x128.png} $out/share/icons/hicolor/128x128/apps/macro-grid.png

          mkdir -p $out/share/icons/hicolor/256x256/apps
          cp ${./icons/256x256.png} $out/share/icons/hicolor/256x256/apps/macro-grid.png
        '';
      };

      devShells.${system}.default = pkgs.mkShell {
        inputsFrom = [ self.packages.${system}.default ];
      };
    };
}