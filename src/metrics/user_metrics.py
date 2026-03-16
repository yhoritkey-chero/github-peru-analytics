from datetime import datetime
from collections import Counter

class UserMetricsCalculator:
    def __init__(self):
        self.today = datetime.now()

    def calculate_all_metrics(self, user: dict, repos: list[dict], classifications: list[dict]) -> dict:
        metrics = {}
        
        # Activity Metrics
        metrics["total_repos"] = len(repos)
        metrics["total_stars_received"] = sum(r.get("stargazers_count", 0) for r in repos)
        metrics["total_forks_received"] = sum(r.get("forks_count", 0) for r in repos)
        metrics["avg_stars_per_repo"] = (
            metrics["total_stars_received"] / metrics["total_repos"]
            if metrics["total_repos"] > 0 else 0
        )
        
        created_at_raw = user.get("created_at", datetime.now().isoformat())
        created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        metrics["account_age_days"] = max(1, (self.today - created_at).days)
        
        metrics["repos_per_year"] = (
            metrics["total_repos"] / (metrics["account_age_days"] / 365.25)
        )
        
        # Influence Metrics
        metrics["followers"] = user.get("followers", 0)
        metrics["following"] = user.get("following", 0)
        metrics["follower_ratio"] = (
            metrics["followers"] / metrics["following"]
            if metrics["following"] > 0 else metrics["followers"]
        )
        metrics["h_index"] = self._calculate_h_index(repos)
        metrics["impact_score"] = (
            metrics["total_stars_received"] + (metrics["total_forks_received"] * 2) + metrics["followers"]
        )
        
        # Technical Metrics
        languages = [r.get("language") for r in repos if r.get("language")]
        lang_counts = Counter(languages)
        metrics["primary_languages"] = [l for l, _ in lang_counts.most_common(3)]
        metrics["language_diversity"] = len(set(languages))
        
        industry_codes = [c["industry_code"] for c in classifications if "industry_code" in c]
        metrics["industries_served"] = len(set(industry_codes))
        metrics["primary_industry"] = Counter(industry_codes).most_common(1)[0][0] if industry_codes else None
        
        # Documentation Quality
        repos_with_readme = sum(1 for r in repos if r.get("has_readme", False) or r.get("readme_content"))
        repos_with_license = sum(1 for r in repos if r.get("license"))
        
        metrics["has_readme_pct"] = repos_with_readme / len(repos) if repos else 0
        metrics["has_license_pct"] = repos_with_license / len(repos) if repos else 0
        
        # Engagement Metrics
        metrics["total_open_issues"] = sum(r.get("open_issues_count", 0) for r in repos)
        
        if repos:
            try:
                # Find the most recent push
                push_dates = []
                for r in repos:
                    pushed_at = r.get("pushed_at")
                    if pushed_at:
                        push_dates.append(datetime.fromisoformat(pushed_at.replace("Z", "+00:00")).replace(tzinfo=None))
                
                if push_dates:
                    last_push = max(push_dates)
                    metrics["days_since_last_push"] = (self.today - last_push).days
                    metrics["is_active"] = metrics["days_since_last_push"] < 90
                else:
                    metrics["days_since_last_push"] = None
                    metrics["is_active"] = False
            except Exception:
                metrics["days_since_last_push"] = None
                metrics["is_active"] = False
        else:
            metrics["days_since_last_push"] = None
            metrics["is_active"] = False
            
        return metrics

    def _calculate_h_index(self, repos: list[dict]) -> int:
        stars = sorted([r.get("stargazers_count", 0) for r in repos], reverse=True)
        h = 0
        for i, s in enumerate(stars):
            if s >= i + 1:
                h = i + 1
            else:
                break
        return h
