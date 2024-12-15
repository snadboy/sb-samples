import asyncio
import logging
import logging.handlers
import os
from datetime import date, datetime
import random
from rich import print as rprint
from dotenv import load_dotenv
from sb_notion_async import AsyncSBNotion
from notion_filters import (
    NotionFilter, NotionFilterType, NotionFilterOperator,
    NotionSort, NotionSortDirection
)
from generated.tv_shows import TvShows
from generated.episodes import Episodes
from generated.seasons import Seasons
from generated.everything_bagel import EverythingBagel

def setup_logger(log_file: str) -> logging.Logger:
    """Set up and configure logger."""
    logger = logging.getLogger("notion_example")
    
    # Create rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10000,  # 10KB per file
        backupCount=3    # Keep 3 backup files
    )
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Set up httpx and notion_client loggers
    # setup_logging()
    
    return logger

async def main():
    """Main function."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the API key from environment variables
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        rprint("[red]Error: NOTION_API_KEY environment variable not set. Please create a .env file based on .env.example[/red]")
        return

    # Initialize the async Notion client
    async with AsyncSBNotion(api_key) as notion:
        # List all databases
        rprint("\n[green]Listing all databases...[/green]")
        databases = await notion.databases
        for db_id, db in databases.items():
            title = db["title"][0]["plain_text"] if db["title"] else "Untitled"
            rprint(f"  - {title} ({db_id})")

        # Get Everything Bagel database
        rprint("\n[green]Getting Everything Bagel database...[/green]")
        db = await notion.get_database("Everything Bagel")
        if not db:
            rprint("[red]Error: Could not find Everything Bagel database[/red]")
            return
        
        rprint(f"Found database with ID: {db['id']}")

        # Create EverythingBagel
        ebda = EverythingBagel(
            name=f'name-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            checkbox=random.random() < 0.3,
            select=EverythingBagel.selectEnum.OPT_2,
            multi_select=[EverythingBagel.multi_selectEnum.MOPT_2, EverythingBagel.multi_selectEnum.MOPT_1],
            status=EverythingBagel.statusEnum.SHOULD_START,
            number=10000 * random.random(),
            person=["John Doe", "Jane Doe"],
            url="https://example.com",
            email="V4xYI@example.com",
            date=date.today(),
            files_media=["file1", "file2"],
            phone="+1234567890",
            status_1=EverythingBagel.statusEnum.NOT_STARTED,
        )
        
        created_page = await notion.create_page(ebda)
        rprint(f"Created page with ID: {created_page['id']} - name: {ebda.name}")

        # Get TV Shows database
        rprint("\n[green]Getting TV Shows database...[/green]")
        tv_shows_id = '14f84b8f-8940-8125-bca9-ecb710ba46c2'  # This is the ID from the generated class
        try:
            db = await notion.client.databases.retrieve(tv_shows_id)
            rprint(f"Found database with ID: {db['id']}")
        except Exception as e:
            rprint(f"[red]Error retrieving TV Shows database: {str(e)}[/red]")
            rprint("[red]Make sure you have access to this database and the API key has the correct permissions.[/red]")
            return

        db_id = db["id"]
        
        # Generate database classes if needed
        await notion.generate_database_class(db_id)

        # Create a filter for Status = "Watching"
        status_filter = NotionFilter(
            type=NotionFilterType.PROPERTY,
            notion_property=TvShows.to_notion_name("status"),
            operator=NotionFilterOperator.EQUALS,
            value=TvShows.statusEnum.WATCHING.value
        )

        # Create a filter for Genre contains "Action"
        genre_filter = NotionFilter(
            type=NotionFilterType.PROPERTY,
            notion_property=TvShows.to_notion_name("genres"),
            operator=NotionFilterOperator.CONTAINS,
            value=TvShows.genresEnum.ACTION.value
        )

        # Query for currently airing shows
        rprint("\n[green]Querying currently airing shows...[/green]")
        currently_airing = NotionFilter(
            type=NotionFilterType.PROPERTY,
            notion_property="Status",  # Use exact property name from schema
            operator=NotionFilterOperator.EQUALS,
            value={"name": TvShows.statusEnum.CONTINUING.value}  # Use dict format for select/status properties
        )
        shows = await notion.query_database(TvShows, filter=currently_airing)
        rprint(f"\nFound {len(shows)} currently airing shows:")
        for show in shows:
            rprint(f"\n[blue]Show: {show.title}[/blue]")
            rprint(f"  Status: {show.status}")
            rprint(f"  Network: {show.network}")
            if show.first_aired:
                rprint(f"  First Aired: {show.first_aired.strftime('%Y-%m-%d')}")
            if show.genres:
                rprint(f"  Genres: {', '.join(show.genres)}")

        # Create a new show
        rprint("\n[green]Creating a new show...[/green]")
        new_show = TvShows(
            title="Test Show (Async)",
            status=TvShows.statusEnum.WATCHING,
            network="Test Network",
            overview="A test show for async demonstration",
            runtime=45.0,
            genres=[TvShows.genresEnum.ACTION, TvShows.genresEnum.DRAMA],
            first_aired=datetime.now()
        )
        created_show = await notion.create_page(new_show)
        rprint(f"Created show with ID: {created_show['id']}")

        # Update the show
        rprint("\n[green]Updating the show...[/green]")
        updated_show = TvShows.from_notion_page(created_show)
        updated_show.status = TvShows.statusEnum.ENDED
        updated_show.overview = "Updated overview for async test show"
        await notion.update_page(created_show["id"], updated_show)
        rprint("Show updated successfully")

        # Demonstrate parallel operations
        rprint("\n[green]Demonstrating parallel operations...[/green]")
        # Get all shows and their first season in parallel
        shows = await notion.query_database(TvShows)
        
        # Create tasks for getting the first season of each show
        tasks = []
        for show in shows[:5]:  # Limit to first 5 shows for demonstration
            show_filter = NotionFilter(
                type=NotionFilterType.PROPERTY,
                notion_property="Show",  # Use exact property name from schema
                operator=NotionFilterOperator.EQUALS,
                value={"contains": show.id}  # Use contains with the ID
            )
            tasks.append(notion.query_database(
                Seasons,
                filter=show_filter
            ))

        # Wait for all tasks to complete
        seasons_results = await asyncio.gather(*tasks)
        
        # Display results
        for show, seasons in zip(shows[:5], seasons_results):
            rprint(f"\n[blue]Show: {show.title}[/blue]")
            if seasons:
                season = seasons[0]  # Just show the first season found
                rprint(f"  First Season: {season.name}")
                rprint(f"  Episodes: {season.episodes}")
                rprint(f"  Status: {season.status}")
            else:
                rprint("  No seasons found")

if __name__ == "__main__":
    asyncio.run(main())
