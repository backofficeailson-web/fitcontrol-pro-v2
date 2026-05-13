/* =============================================================================
 * FitControl Pro 2.0 — PWA bootstrap
 * Registers the service worker and surfaces the install prompt.
 * =========================================================================== */
(function () {
  'use strict';

  // Only run in browsers that support SW and not inside the dev server iframe
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker
        .register('/service-worker.js', { scope: '/' })
        .then(function (reg) {
          console.log('[PWA] Service worker registered:', reg.scope);
        })
        .catch(function (err) {
          console.warn('[PWA] Service worker registration failed:', err);
        });
    });
  }

  // ---------- Install prompt (Android/Chrome) ----------
  let deferredPrompt = null;
  const installBtn = document.getElementById('pwa-install-btn');

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) {
      installBtn.hidden = false;
      installBtn.addEventListener('click', async function () {
        installBtn.disabled = true;
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log('[PWA] Install outcome:', outcome);
        deferredPrompt = null;
        installBtn.hidden = true;
      });
    }
  });

  window.addEventListener('appinstalled', function () {
    console.log('[PWA] App installed');
    if (installBtn) installBtn.hidden = true;
  });

  // ---------- iOS install hint ----------
  // iOS Safari doesn't fire beforeinstallprompt; show a small banner once.
  const isIos = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
  const inStandalone =
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;
  if (isIos && !inStandalone && !localStorage.getItem('fc-ios-hint-dismissed')) {
    document.addEventListener('DOMContentLoaded', function () {
      const banner = document.createElement('div');
      banner.className = 'pwa-ios-banner';
      banner.innerHTML =
        '<span>Para instalar o FitControl no iPhone: toque em ' +
        '<strong>Compartilhar</strong> e depois em ' +
        '<strong>Adicionar à Tela de Início</strong>.</span>' +
        '<button type="button" aria-label="Fechar">×</button>';
      document.body.appendChild(banner);
      banner.querySelector('button').addEventListener('click', function () {
        banner.remove();
        localStorage.setItem('fc-ios-hint-dismissed', '1');
      });
    });
  }
})();
