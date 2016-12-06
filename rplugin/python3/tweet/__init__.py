import neovim


@neovim.plugin
class TestPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.command("Hello")
    def hello(self):
        self.nvim.current.line = "Hello!!!!!!!!!"
