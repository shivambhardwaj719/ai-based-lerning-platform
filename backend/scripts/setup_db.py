"""Database initialization script: creates tables, sets up indices, seeds data."""
from __future__ import annotations

import asyncio
import click


async def init_db() -> None:
    from core.database import database_manager
    from core.elasticsearch import es_manager

    await database_manager.connect()
    await es_manager.connect()

    click.echo("Creating database tables...")
    await database_manager.create_all_tables()

    click.echo("Setting up Elasticsearch indices...")
    await es_manager.setup_indices()

    await database_manager.disconnect()
    await es_manager.disconnect()
    click.echo("✅ Database initialization complete!")


async def seed_data() -> None:
    """Seed initial data: plans, sample problems."""
    from core.database import database_manager
    await database_manager.connect()
    async with database_manager.session() as db:
        from repositories.payment_repository import PlanRepository
        plan_repo = PlanRepository(db)
        await plan_repo.create(
            name="Free", slug="free", tier="free",
            price_monthly=0.0, price_yearly=0.0,
            features=["10 problems/day", "Basic AI mentor", "Community access"],
        )
        await plan_repo.create(
            name="Pro", slug="pro", tier="pro",
            price_monthly=9.99, price_yearly=99.99,
            features=["Unlimited problems", "Advanced AI mentor", "Contests", "Labs"],
        )
        click.echo("✅ Seed data inserted!")
    await database_manager.disconnect()


@click.group()
def cli():
    pass


@cli.command()
def init():
    asyncio.run(init_db())


@cli.command()
def seed():
    asyncio.run(seed_data())


@cli.command()
def setup():
    asyncio.run(init_db())
    asyncio.run(seed_data())


if __name__ == "__main__":
    cli()
