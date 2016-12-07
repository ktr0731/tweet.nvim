import urllib
import urllib2

import neovim


@neovim.plugin
class TestPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.params = {
                    'oauth_token': '',
                }

    @neovim.command('Tweet', nargs='*')
    def hello(self, lines):
        end_point = 'https://api.twitter.com/1.1/statuses/update.json'

        content = ''
        for line in lines:
            content += line + '\n'

        params = this.params
        params.update({'status': content})

        req = urllib2.Request(end_point)
        req.add_header('application/x-www-form-urlencoded')
        req.add_data(urllib.urlencode(params))
        res = urllib2.urlopen(req)

        self.nvim.current.line = 'Hello!!!!{0}'.format(content)
