#!/usr/bin/env python3
"""
Hermes Deploy - Multi-Tier Deployment Script
Deploys to GitHub Pages, Netlify, or Vercel
"""

import json
import sys
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class DeployConfig:
    target: Literal["github-pages", "netlify", "vercel"] = "github-pages"
    site_id: str = ""
    dist_dir: Path = Path("dist")
    github_repo: str = "unplug-netizen/hermes-sites"
    netlify_site_id: Optional[str] = None
    vercel_project_id: Optional[str] = None

class DeployManager:
    """Manages deployment to multiple hosting providers"""
    
    def __init__(self, config: DeployConfig):
        self.config = config
        self.site_dir = Path("clients") / config.site_id
        self.dist_dir = self.site_dir / "dist"
    
    def deploy(self) -> dict:
        """Deploy site to configured target"""
        
        if not self.dist_dir.exists():
            print(f"❌ Dist-Verzeichnis nicht gefunden: {self.dist_dir}")
            return {"success": False, "error": "Dist not found"}
        
        deploy_methods = {
            "github-pages": self._deploy_github_pages,
            "netlify": self._deploy_netlify,
            "vercel": self._deploy_vercel
        }
        
        deploy_fn = deploy_methods.get(self.config.target)
        if not deploy_fn:
            return {"success": False, "error": f"Unknown target: {self.config.target}"}
        
        return deploy_fn()
    
    def _deploy_github_pages(self) -> dict:
        """Deploy to GitHub Pages"""
        try:
            # Create gh-pages branch if not exists
            result = subprocess.run(
                ["git", "branch", "--list", "gh-pages"],
                capture_output=True, text=True, cwd="/root/hermes-sites"
            )
            
            if "gh-pages" not in result.stdout:
                subprocess.run(
                    ["git", "checkout", "--orphan", "gh-pages"],
                    capture_output=True, cwd="/root/hermes-sites"
                )
                subprocess.run(
                    ["git", "rm", "-rf", "."],
                    capture_output=True, cwd="/root/hermes-sites"
                )
            else:
                subprocess.run(
                    ["git", "checkout", "gh-pages"],
                    capture_output=True, cwd="/root/hermes-sites"
                )
            
            # Copy dist content
            site_dir = Path(self.config.site_id)
            site_dir.mkdir(exist_ok=True)
            
            # Clear old content
            for item in site_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            
            # Copy new content
            for item in self.dist_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, site_dir)
                elif item.is_dir():
                    shutil.copytree(item, site_dir / item.name, dirs_exist_ok=True)
            
            # Create index.html redirect
            index_file = Path("index.html")
            index_file.write_text(f"""<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0;url=./{self.config.site_id}/"></head>
<body><p>Redirecting to <a href="./{self.config.site_id}/">{self.config.site_id}</a>...</p></body>
</html>""")
            
            # Commit and push
            subprocess.run(["git", "add", "."], capture_output=True, cwd="/root/hermes-sites")
            subprocess.run(
                ["git", "commit", "-m", f"🚀 Deploy {self.config.site_id}"],
                capture_output=True, cwd="/root/hermes-sites"
            )
            subprocess.run(
                ["git", "push", "origin", "gh-pages", "--force"],
                capture_output=True, cwd="/root/hermes-sites"
            )
            
            # Switch back to main
            subprocess.run(
                ["git", "checkout", "main"],
                capture_output=True, cwd="/root/hermes-sites"
            )
            
            url = f"https://unplug-netizen.github.io/hermes-sites/{self.config.site_id}/"
            print(f"✅ Deployed to GitHub Pages: {url}")
            return {"success": True, "url": url, "target": "github-pages"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_netlify(self) -> dict:
        """Deploy to Netlify"""
        try:
            if not shutil.which("netlify"):
                subprocess.run(["npm", "install", "-g", "netlify-cli"], capture_output=True)
            
            site_id = self.config.netlify_site_id or self.config.site_id
            
            result = subprocess.run(
                [
                    "netlify", "deploy",
                    "--prod",
                    "--dir", str(self.dist_dir),
                    "--site", site_id
                ],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Extract URL from output
                url = f"https://{site_id}.netlify.app"
                print(f"✅ Deployed to Netlify: {url}")
                return {"success": True, "url": url, "target": "netlify"}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_vercel(self) -> dict:
        """Deploy to Vercel"""
        try:
            if not shutil.which("vercel"):
                subprocess.run(["npm", "install", "-g", "vercel"], capture_output=True)
            
            result = subprocess.run(
                ["vercel", "--prod", "--yes", "--cwd", str(self.dist_dir)],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                url = f"https://{self.config.site_id}.vercel.app"
                print(f"✅ Deployed to Vercel: {url}")
                return {"success": True, "url": url, "target": "vercel"}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_deployment(self, url: str) -> dict:
        """Verify deployment is accessible"""
        import urllib.request
        try:
            response = urllib.request.urlopen(url, timeout=10)
            status = response.getcode()
            return {
                "accessible": status == 200,
                "status_code": status,
                "url": url
            }
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e),
                "url": url
            }


def main():
    """CLI for deployment"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Deploy Manager")
    parser.add_argument("--site", required=True, help="Site ID to deploy")
    parser.add_argument("--target", choices=["github-pages", "netlify", "vercel"],
                        default="github-pages", help="Deployment target")
    parser.add_argument("--netlify-id", help="Netlify site ID")
    parser.add_argument("--vercel-id", help="Vercel project ID")
    
    args = parser.parse_args()
    
    config = DeployConfig(
        target=args.target,
        site_id=args.site,
        netlify_site_id=args.netlify_id,
        vercel_project_id=args.vercel_id
    )
    
    manager = DeployManager(config)
    result = manager.deploy()
    
    if result["success"]:
        print(f"\n🌐 Live URL: {result['url']}")
        
        # Verify
        verify = manager.verify_deployment(result["url"])
        if verify["accessible"]:
            print(f"✅ Site verified and accessible")
        else:
            print(f"⚠️  Site may need a moment to propagate")
    else:
        print(f"❌ Deployment failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
