package org.nethserver.keycloak.home;

import org.keycloak.Config;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.services.resource.RealmResourceProvider;
import org.keycloak.services.resource.RealmResourceProviderFactory;

/** Serves HomeRedirect at /realms/{realm}/ns8-home. */
public final class HomeRedirectFactory implements RealmResourceProviderFactory {
    public static final String ID = "ns8-home";
    @Override public RealmResourceProvider create(KeycloakSession session) { return new HomeRedirect(session); }
    @Override public String getId() { return ID; }
    @Override public void init(Config.Scope config) { }
    @Override public void postInit(KeycloakSessionFactory factory) { }
    @Override public void close() { }
}
