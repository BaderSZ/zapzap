from PyQt6.QtCore import QEvent, Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QApplication
from zapzap import __whatsapp_url__
from zapzap.services.portal_config import get_setting

# Classe para a página do webapp.
class WhatsApp(QWebEnginePage):

    link_url = ''

    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        # Ativa o EventFilter
        QApplication.instance().installEventFilter(self)

        # Acionar a resposta de permissão do recurso.
        self.featurePermissionRequested.connect(self.permission)

        # Este sinal é emitido quando o mouse passa sobre um link
        self.linkHovered.connect(self.link_hovered)

        self.loadFinished.connect(self.load_finished)
       

    def load_finished(self, flag):
        # Ativa a tela cheia para telas de proporção grande no WhatsApp Web.
        if flag:
            self.runJavaScript("""
                const checkExist = setInterval(() => {
                    const classElement = document.getElementsByClassName("_1XkO3")[0];
                    if (classElement != null) {
                        classElement.style = 'width: 100vw; height: 100vh; position: unset'
                        clearInterval(checkExist);
                    }
                }, 100);

                 const checkNotify = setInterval(() => {
                    const classElement = document.evaluate('//*[@id="side"]/span/div/div', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (classElement != null) {
                        classElement.click()
                        clearInterval(checkNotify);
                    }
                }, 100);
            """)

            if get_setting('night_mode'):
                self.setTheme('dark')

    def setTheme(self, theme):
        if theme == 'light':  # light
            self.runJavaScript(
                "document.body.classList.remove('dark')")
        else:  # dark
            self.runJavaScript("document.body.classList.add('dark')")

    def link_hovered(self, url):
        # url contém o URL de destino do link. Ao mover o mouse para fora da url o seu valor é definido como uma string vazia
        self.link_url = url

    def permission(self, frame, feature):
        self.setFeaturePermission(
            frame, feature,  QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    # Abrindo links no navegador padrão do usuário
    # Solução alternativa ao acceptNavigationRequest, pois não funcionou dentro do whatsapp.
    # Mapeia os eventos do Mouse e abre o link a partir do capturado do signal linkHovered.
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.link_url != '' and self.link_url != __whatsapp_url__:
                    QDesktopServices.openUrl(QUrl(self.link_url))
                    return True
        return False
