<template>
  <v-app>
    <!-- Navigation Bar -->
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>HRMS</v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- Show Logout if token exists -->
      <div>
        <v-btn text @click="goToDashboard()">Dashboard</v-btn>
      </div>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>

export default {
  name: 'App',
  methods: {
    goToDashboard() {
      this.$router.push('/dashboard')
    }
  }
}
</script>