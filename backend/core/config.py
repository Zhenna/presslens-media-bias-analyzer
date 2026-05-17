from pydantic_settings import BaseSettings
from backend.models.schemas import Outlet


class Settings(BaseSettings):
    app_name: str = "PressLens"
    cache_ttl_seconds: int = 900  # 15 min
    max_articles_per_outlet: int = 3
    request_timeout_seconds: int = 15

    class Config:
        env_file = ".env"


settings = Settings()


OUTLETS: list[Outlet] = [
    Outlet(id="nyt",       name="NY Times",     region="US",  lean="center-left",  language="en", rss="https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    Outlet(id="fox",       name="Fox News",     region="US",  lean="right",        language="en", rss="https://moxie.foxnews.com/google-publisher/world.xml"),
    Outlet(id="bbc",       name="BBC",          region="UK",  lean="center",       language="en", rss="http://feeds.bbci.co.uk/news/world/rss.xml"),
    Outlet(id="guardian",  name="The Guardian", region="UK",  lean="left",         language="en", rss="https://www.theguardian.com/world/rss"),
    Outlet(id="aljazeera", name="Al Jazeera",   region="ME",  lean="Qatar state",  language="en", rss="https://www.aljazeera.com/xml/rss/all.xml"),
    Outlet(id="rt",        name="RT",           region="RU",  lean="state",        language="en", rss="https://www.rt.com/rss/news/"),
    Outlet(id="cgtn",      name="CGTN",         region="CN",  lean="state",        language="en", rss="https://www.cgtn.com/subscribe/rss/section/world.xml"),
    Outlet(id="lemonde",   name="Le Monde",     region="FR",  lean="center-left",  language="fr", rss="https://www.lemonde.fr/rss/une.xml"),
    Outlet(id="spiegel",   name="Der Spiegel",  region="DE",  lean="center-left",  language="de", rss="https://www.spiegel.de/international/index.rss"),
    Outlet(id="reuters",   name="Reuters",      region="INT", lean="center",       language="en", rss="https://feeds.reuters.com/reuters/worldNews"),
    Outlet(id="ndtv",      name="NDTV",         region="IN",  lean="center",       language="en", rss="https://feeds.feedburner.com/ndtvnews-world-news"),
    Outlet(id="telesur",   name="Telesur",      region="LA",  lean="left",         language="es", rss="https://www.telesurenglish.net/rss/"),
]

OUTLET_MAP: dict[str, Outlet] = {o.id: o for o in OUTLETS}
