<template>
  <v-form @submit.prevent="submit">
    <v-text-field label="Name" v-model="form.name" required />
    <v-text-field label="Email" v-model="form.email" required />
    <v-text-field label="Department" v-model="form.department" required />
    <v-text-field label="Designation" v-model="form.designation" />
    <v-select
      :items="languages"
      label="Preferred Language"
      v-model="form.preferred_language"
    />
    <v-btn color="primary" type="submit">Add Employee</v-btn>
  </v-form>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      form: {
        name: '',
        email: '',
        department: '',
        designation: '',
        preferred_language: 'en'
      },
      languages: ['en', 'hi', 'fr']
    }
  },
  methods: {
    async submit() {
      try {
        // await axios.post('http://127.0.0.1:5000/api/employees', this.form)
        await axios.post('https://hrms-4jys.onrender.com/api/employees', this.form)
        this.$emit('employee-added')
        this.form = {
          name: '',
          email: '',
          department: '',
          designation: '',
          preferred_language: 'en'
        }
      } catch (e) {
        alert('Error adding employee')
      }
    }
  }
}
</script>
