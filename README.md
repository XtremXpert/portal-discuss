# portal-discuss

Discuss pour utilisateurs portail — modules atomiques (Odoo 19, AGPL-3) :

| Module | Rôle |
|---|---|
| `portal_discuss_channel` | Accès des portail aux canaux de groupe dont ils sont membres (règles d'enregistrement; le cœur ne connaît que group_public_id) |
| `portal_discuss_dm` | Messages privés : liste /my/chats, démarrage d'une conversation, point d'extension `_portal_discuss_can_message()` |
| `portal_discuss_nav` | Barre de retour configurable sur la page Discuss publique (paramètres `portal_discuss.nav_url` / `nav_label`) |

Le clavardage lui-même est la page Discuss publique native (`/discuss/channel/<id>`) — historique, envoi, appels WebRTC. Patron issu de diverse-cité (chats 1:1), généralisé aux canaux de groupe pour Les Maisons d'à côté. Chaque module s'installe seul : l'installation est la configuration.
