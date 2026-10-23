(() => {
  const password = document.getElementById('id_password');
  const toggle = document.getElementById('password-toggle');
  toggle?.addEventListener('click', () => {
    const show = password.type === 'password';
    password.type = show ? 'text' : 'password';
    toggle.textContent = show ? '隱藏' : '顯示';
    toggle.setAttribute('aria-pressed', String(show));
  });
  document.getElementById('id_username')?.setAttribute('autocomplete', 'username');
  password?.setAttribute('autocomplete', 'current-password');
  const button = document.getElementById('captcha-reload-btn');
  const image = document.querySelector('.signin-captcha .captcha');
  const status = document.getElementById('captcha-status');
  async function refresh() {
    if (button.disabled) return;
    button.disabled = true;
    status.textContent = '';
    try {
      const response = await fetch('/captcha/refresh/', {headers: {'X-Requested-With': 'XMLHttpRequest'}, cache: 'no-store'});
      if (!response.ok) throw new Error();
      const data = await response.json();
      image.src = data.image_url;
      document.querySelector('input[name="captcha_0"]').value = data.key;
      const answer = document.getElementById('id_captcha_1');
      answer.value = '';
      answer.focus();
      status.textContent = '驗證碼已更新。';
    } catch (_) {
      status.textContent = '驗證碼更新失敗，請再試一次或重新整理頁面。';
    } finally {
      button.disabled = false;
    }
  }
  button?.addEventListener('click', refresh);
  image?.addEventListener('click', refresh);
  image?.setAttribute('alt', '圖片驗證碼，可使用換一張按鈕更新');
})();
