import click
from dipcalc.adjudicator import Adjudicator


@click.group()
@click.option(
    "--variant",
    default="default",
    help="Name of a default variant, or a path to a variant folder.",
)
@click.option(
    "--start-positions",
    default=False,
    help="Will load the default unit positions for this variant.",
)
@click.pass_context
def cli(context, variant, start_positions):
    context.ensure_object(dict)
    adj = Adjudicator(variant)

    if start_positions:
        adj.place_default()

    context.obj["adj"] = adj


@cli.command(help="Test the validity of a unit move/attack.")
@click.pass_context
@click.argument("unit_type")
@click.argument("a")
@click.argument("b")
@click.argument("faction_code", default=None, required=False)
def move(context, unit_type: str, a: str, b: str, faction_code: str = None):
    adj: Adjudicator = context.obj["adj"]
    is_valid = adj.validate_move(unit_type, a, b, faction_code)
    territory_a = adj.territories.nodes[a]
    territory_b = adj.territories.nodes[b]
    faction = None
    if faction_code is not None:
        faction = adj.factions[faction_code]

    title = click.style(" ORDERS ".center(60, "#"))
    click.echo(title)

    if faction is not None:
        click.echo(f"[{faction['name'].upper()}]")

    status = click.style("[INVALID]".rjust(15), fg="red")
    if is_valid:
        status = click.style("[VALID]".rjust(15), fg="blue")

    a_name = f"{territory_a['code'].upper()} ({territory_a['name'][:14]})"
    b_name = f"{territory_b['code'].upper()} ({territory_b['name'][:14]})"

    line = unit_type.upper() + "  "
    line += a_name.ljust(21)
    line += b_name.ljust(21)
    line += status
    click.echo(line)
