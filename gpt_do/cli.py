import click


def get_doer(model):
    if model == "chatgpt":
        from gpt_do.doers.pywright_doer import PywrightDoer

        return PywrightDoer
    elif model == "gpt3":
        from gpt_do.doers.gpt3_doer import GPT3Doer

        GPT3Doer.model = "text-davinci-003"
        return GPT3Doer
    elif model == "codex":
        from gpt_do.doers.gpt3_doer import GPT3Doer

        GPT3Doer.model = "code-davinci-002"
        return GPT3Doer
    else:
        raise ValueError(f"Unknown model {model}")


@click.command()
@click.argument("request", required=True, nargs=-1)
@click.option("--debug", is_flag=True)
@click.option("--yes", "-y", is_flag=True, help="Do not ask for confirmation")
@click.option(
    "--model",
    default="gpt3",
    type=click.Choice(
        ["gpt3", "codex", "chatgpt"],
        case_sensitive=False,
    ),
)
def do(request: str, debug: bool, yes: bool, model: str):
    """Fetches and executes commands in your shell based on the advice of GPT3."""
    do = get_doer(model)(debug=debug)
    response = do.query(" ".join(request))
    click.echo(click.style(response["explanation"], bold=True))

    script = "\n".join(response["commands"])
    if len(script) == 0:
        return

    click.echo(click.style(script, fg="green"))

    if yes:
        res = "y" 
    else: 
        res = click.prompt("Execute this command(y) or edit(e) it?", 
                           type=click.Choice(("y", "e", "N"), 
                           case_sensitive=False), show_choices=True)

    if res == "e":
        if edited := click.edit(script, require_save=True, extension=".sh"):
            script = edited 
        else:
            # if user does not save we do not run the command
            res = "N"

    if res != "N":
        do.execute(script)


if __name__ == "__main__":
    do()
