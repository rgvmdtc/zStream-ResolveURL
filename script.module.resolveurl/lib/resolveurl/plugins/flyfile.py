"""
    Plugin for ResolveURL
    Copyright (C) 2026 icarok99

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class FlyFileResolver(ResolveUrl):
    name = 'FlyFile'
    # flyf.lat is a newer front-end skin; both share the api.flyfile.app backend.
    domains = ['flyfile.app', 'flyf.lat']
    pattern = r'(?://|\.)(flyfile\.app|flyf\.lat)/(?:embed|v)/([A-Za-z0-9]+)'
    api_host = 'api.flyfile.app'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.RAND_UA,
            'Referer': web_url,
            'Origin': urllib_parse.urljoin(web_url, '/')[:-1]
        }
        # The assign backend is always api.flyfile.app regardless of the front domain.
        assign_url = 'https://{0}/api/streaming/assign/{1}'.format(self.api_host, media_id)
        data = self.net.http_GET(assign_url, headers=headers).json
        if data.get('url') and data.get('token'):
            stream_url = '{0}/hls/{1}/master.m3u8'.format(
                data['url'].rstrip('/'),
                data['token']
            )
            return stream_url + helpers.append_headers(headers)

        raise ResolverError('File Not Found or Removed')

    def get_url(self, host, media_id):
        template = 'https://{host}/v/{media_id}' if host == 'flyf.lat' else 'https://{host}/embed/{media_id}'
        return self._default_get_url(host, media_id, template=template)
