<template>
  <v-form @submit.prevent="submit">
    <v-text-field label="Purpose Name" v-model="form.name" required />
    <v-text-field label="Description" v-model="form.description" />
    <v-text-field label="Departments (comma-separated)" v-model="form.departments" />
    <v-select :items="languages" label="Language" v-model="form.language" />
    <v-btn color="secondary" type="submit">Add Purpose</v-btn>
  </v-form>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        name: '',
        description: '',
        departments: '',
        language: 'en'
      },
      languages: ['en', 'hi', 'fr']
    }
  },
  methods: {
    async submit() {
      try {
        // await axios.post('http://127.0.0.1:5000/api/purposes', this.form)
        await axios.post('https://hrms-ocfa.onrender.com/api/purposes', this.form)
        this.$emit('purpose-added')
        this.form = { name: '', description: '', departments: '', language: 'en' }
      } catch (e) {
        alert('Error adding purpose')
      }
    }
  }
}
</script>