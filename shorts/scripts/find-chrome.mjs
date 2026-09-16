import fs from 'node:fs';
import path from 'node:path';

/**
 * Bu ortamda Remotion kendi Chrome Headless Shell'ini indiremiyor
 * (remotion.media ag politikasinda yok). Kurulu binary'yi bulur.
 *
 * headless_shell once denenir: tam Chrome binary'sinde eski headless modu
 * kaldirildigi icin Remotion onu baslatamaz.
 *
 * REMOTION_BROWSER_EXECUTABLE ortam degiskeni ile elle gecilebilir.
 *
 * @returns {string | null}
 */
export const findLocalChrome = () => {
  const explicit = process.env.REMOTION_BROWSER_EXECUTABLE;
  if (explicit && fs.existsSync(explicit)) return explicit;

  const root = '/opt/pw-browsers';
  const shells = [];
  const fulls = [];
  if (fs.existsSync(root)) {
    for (const entry of fs.readdirSync(root)) {
      shells.push(path.join(root, entry, 'chrome-linux', 'headless_shell'));
      fulls.push(path.join(root, entry, 'chrome-linux', 'chrome'));
    }
  }
  fulls.push('/usr/bin/chromium', '/usr/bin/google-chrome');

  return [...shells, ...fulls].find((c) => fs.existsSync(c)) ?? null;
};
