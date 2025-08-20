<template>
    <v-app>
      <!-- Navigation Bar -->
      <!-- <v-app-bar app color="primary" dark>
        <v-toolbar-title>DPIA Approval System</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn color="white" @click="goToLogin">Login</v-btn>
      </v-app-bar> -->
  
      <!-- Main Content -->
      <v-container class="fill-height">
        <v-row align="center" justify="center">
          <v-col cols="12" md="8" class="text-center">
            <h1 class="text-h3 font-weight-bold">Welcome to HRMS Tool</h1>
            <p class="text-h5 mt-4">
              Streamline your HRMS Operations with our secure and automated workflow system.
            </p>
          </v-col>
        </v-row>
      </v-container>
    </v-app>
  </template>
  
  <script>
  export default {
    methods: {},
  };
  </script>
  
  <style scoped>
  .v-container {
    min-height: 80vh;
  }
  </style>