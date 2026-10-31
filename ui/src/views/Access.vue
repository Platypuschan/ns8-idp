<!--
  Copyright (C) 2026 Nethesis S.r.l.
  SPDX-License-Identifier: GPL-3.0-or-later
-->
<template>
  <cv-grid fullWidth>
    <cv-row>
      <cv-column class="page-title">
        <h2>{{ $t("access.title") }}</h2>
      </cv-column>
    </cv-row>
    <cv-row>
      <cv-column>
        <p class="mg-bottom-lg">{{ $t("access.description") }}</p>
      </cv-column>
    </cv-row>
    <cv-row v-if="error.listRealms">
      <cv-column>
        <NsInlineNotification
          kind="error"
          :title="$t('action.list-realms')"
          :description="error.listRealms"
          :showCloseButton="false"
        />
      </cv-column>
    </cv-row>
    <cv-row v-if="loading.listRealms">
      <cv-column>
        <cv-tile light>
          <cv-skeleton-text :paragraph="true" :line-count="4" />
        </cv-tile>
      </cv-column>
    </cv-row>
    <cv-row v-else-if="!realms.length && !error.listRealms">
      <cv-column>
        <cv-tile light>
          <NsEmptyState :title="$t('access.no_clients')">
            <template #description>{{
              $t("access.no_clients_description")
            }}</template>
          </NsEmptyState>
        </cv-tile>
      </cv-column>
    </cv-row>
    <cv-row v-for="realm in realms" :key="realm.name">
      <cv-column>
        <cv-tile light class="mg-bottom-lg">
          <h4 class="mg-bottom-md">{{ realm.name }}</h4>
          <NsInlineNotification
            v-if="!realm.user_domain_found"
            kind="warning"
            :title="$t('access.user_domain_not_found')"
            :showCloseButton="false"
          />
          <NsInlineNotification
            v-if="groupErrors[realm.name]"
            kind="error"
            :title="$t('action.list-domain-groups')"
            :description="groupErrors[realm.name]"
            :showCloseButton="false"
          />
          <p v-if="!realm.clients.length">{{ $t("access.no_clients") }}</p>
          <div
            v-for="client in realm.clients"
            :key="client.client_id"
            class="client mg-bottom-lg"
          >
            <div class="client-header mg-bottom-sm">
              <strong>{{ client.client_id }}</strong>
              <cv-tag
                v-if="!client.enabled"
                kind="high-contrast"
                :label="$t('access.client_disabled')"
              />
              <cv-tag
                v-if="client.access_group"
                kind="green"
                :label="
                  $t('access.restricted_to', { group: client.access_group })
                "
              />
              <cv-tag v-else kind="gray" :label="$t('access.unrestricted')" />
            </div>
            <cv-form @submit.prevent="saveClient(realm, client)">
              <cv-select
                :label="$t('access.access_group')"
                v-model="selection[key(realm, client)]"
                :disabled="busy(realm, client) || !groups[realm.name]"
                :invalid-message="errors[key(realm, client)]"
                :helper-text="$t('access.access_group_helper')"
              >
                <cv-select-option value="">{{
                  $t("access.no_restriction")
                }}</cv-select-option>
                <cv-select-option
                  v-for="group in groups[realm.name] || []"
                  :key="group"
                  :value="group"
                  >{{ group }}</cv-select-option
                >
              </cv-select>
              <NsButton
                kind="primary"
                size="field"
                :icon="Save20"
                :loading="saving[key(realm, client)]"
                :disabled="busy(realm, client) || !changed(realm, client)"
                >{{ $t("access.save") }}</NsButton
              >
              <NsButton
                kind="secondary"
                size="field"
                type="button"
                class="check-button"
                :loading="checking[key(realm, client)]"
                :disabled="busy(realm, client) || !client.access_group"
                @click="checkClient(realm, client)"
                >{{ $t("access.check") }}</NsButton
              >
            </cv-form>
            <NsInlineNotification
              v-if="results[key(realm, client)]"
              :kind="results[key(realm, client)].kind"
              :title="results[key(realm, client)].title"
              :description="results[key(realm, client)].description"
              :showCloseButton="false"
            />
          </div>
        </cv-tile>
      </cv-column>
    </cv-row>
  </cv-grid>
</template>

<script>
import to from "await-to-js";
import { mapState } from "vuex";
import {
  QueryParamService,
  UtilService,
  TaskService,
  IconService,
  PageTitleService,
} from "@nethserver/ns8-ui-lib";

export default {
  name: "Access",
  mixins: [
    TaskService,
    IconService,
    UtilService,
    QueryParamService,
    PageTitleService,
  ],
  pageTitle() {
    return this.$t("access.title") + " - " + this.appName;
  },
  data() {
    return {
      q: {
        page: "access",
      },
      urlCheckInterval: null,
      realms: [],
      // Group names of each realm, from its user domain
      groups: {},
      groupErrors: {},
      // Selected group of each client, by realm/client key
      selection: {},
      saving: {},
      checking: {},
      errors: {},
      results: {},
      loading: {
        listRealms: false,
      },
      error: {
        listRealms: "",
      },
    };
  },
  computed: {
    ...mapState(["instanceName", "core", "appName"]),
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.watchQueryData(vm);
      vm.urlCheckInterval = vm.initUrlBindingForApp(vm, vm.q.page);
    });
  },
  beforeRouteLeave(to, from, next) {
    clearInterval(this.urlCheckInterval);
    next();
  },
  created() {
    this.listRealms();
  },
  methods: {
    key(realm, client) {
      return realm.name + "/" + client.client_id;
    },
    busy(realm, client) {
      const key = this.key(realm, client);
      return Boolean(this.saving[key] || this.checking[key]);
    },
    changed(realm, client) {
      return (
        (this.selection[this.key(realm, client)] || "") !==
        (client.access_group || "")
      );
    },
    // Run a task and resolve with its output. A validation failure rejects
    // with the list of validation errors, other failures with a message.
    runTask(action, data, cluster = false) {
      return new Promise((resolve, reject) => {
        const eventId = this.getUuid();
        this.core.$root.$once(`${action}-aborted-${eventId}`, () =>
          reject(this.$t("error.generic_error"))
        );
        this.core.$root.$once(
          `${action}-validation-failed-${eventId}`,
          (validationErrors) => reject(validationErrors)
        );
        this.core.$root.$once(
          `${action}-completed-${eventId}`,
          (taskContext, taskResult) => resolve(taskResult.output)
        );
        const task = {
          action,
          data,
          extra: {
            title: this.$t("action." + action),
            isNotificationHidden: true,
            eventId,
          },
        };
        const created = cluster
          ? this.createClusterTaskForApp(task)
          : this.createModuleTaskForApp(this.instanceName, task);
        to(created).then(([err]) => {
          if (err) {
            console.error(`error creating task ${action}`, err);
            reject(this.getErrorMessage(err));
          }
        });
      });
    },
    errorText(error) {
      if (Array.isArray(error)) {
        return error.map((e) => this.$t("access.error_" + e.error)).join(" ");
      }
      return String(error);
    },
    async listRealms() {
      this.loading.listRealms = true;
      this.error.listRealms = "";
      const [err, output] = await to(this.runTask("list-realms", {}));
      this.loading.listRealms = false;
      if (err) {
        this.error.listRealms = this.errorText(err);
        return;
      }
      this.realms = output.realms;
      for (const realm of this.realms) {
        for (const client of realm.clients) {
          this.$set(
            this.selection,
            this.key(realm, client),
            client.access_group || ""
          );
        }
        if (realm.user_domain_found && !this.groups[realm.name]) {
          this.listGroups(realm);
        }
      }
    },
    async listGroups(realm) {
      this.$set(this.groupErrors, realm.name, "");
      const [err, output] = await to(
        this.runTask("list-domain-groups", { domain: realm.name }, true)
      );
      if (err) {
        this.$set(this.groupErrors, realm.name, this.errorText(err));
        return;
      }
      const names = output.groups.map((g) => g.group).sort();
      // Keep a configured group selectable, even if it is gone from LDAP
      for (const client of realm.clients) {
        if (client.access_group && !names.includes(client.access_group)) {
          names.push(client.access_group);
        }
      }
      this.$set(this.groups, realm.name, names);
    },
    async saveClient(realm, client) {
      const key = this.key(realm, client);
      const group = this.selection[key] || null;
      this.$set(this.errors, key, "");
      this.$set(this.results, key, null);
      this.$set(this.saving, key, true);
      const [err] = await to(
        this.runTask("alter-realm-client", {
          domain: realm.name,
          client_id: client.client_id,
          access_group: group,
        })
      );
      this.$set(this.saving, key, false);
      if (err) {
        this.$set(this.errors, key, this.errorText(err));
        return;
      }
      client.access_group = group;
      this.$set(this.results, key, {
        kind: "success",
        title: group
          ? this.$t("access.saved_restricted", { group })
          : this.$t("access.saved_unrestricted"),
        description: "",
      });
      if (group) {
        this.checkClient(realm, client);
      }
    },
    async checkClient(realm, client) {
      const key = this.key(realm, client);
      this.$set(this.checking, key, true);
      const [err, state] = await to(
        this.runTask("get-client-access", {
          domain: realm.name,
          client_id: client.client_id,
          live: true,
        })
      );
      this.$set(this.checking, key, false);
      if (err) {
        this.$set(this.results, key, {
          kind: "error",
          title: this.$t("access.check_failed"),
          description: this.errorText(err),
        });
        return;
      }
      const issues = state.issues.concat(state.live ? state.live.issues : []);
      if (state.enforced && state.enabled && state.live && state.live.ok) {
        this.$set(this.results, key, {
          kind: "success",
          title: this.$t("access.check_ok", { group: state.group }),
          description: "",
        });
      } else {
        if (!state.enabled) {
          issues.unshift("client_disabled");
        }
        this.$set(this.results, key, {
          kind: "warning",
          title: this.$t("access.check_issues"),
          description: issues
            .map((issue) => this.$t("access.issue_" + issue))
            .join(" "),
        });
      }
    },
  },
};
</script>

<style scoped lang="scss">
@import "../styles/carbon-utils";

.client-header {
  display: flex;
  align-items: center;
  gap: $spacing-03;
}

.cv-form .bx--form-item {
  margin-bottom: $spacing-05;
}

.check-button {
  margin-left: $spacing-03;
}
</style>
