<!-- <template>
  <v-container>
    <h2>HRMS Dashboard</h2>

    <v-btn color="primary" class="mt-4" @click="goToRegister">
      Register New Employee
    </v-btn>

    <v-btn color="error" class="mt-4 ml-2" @click="runCleanup">
      Run Retention Cleanup
    </v-btn>

    <v-alert v-if="cleanupMessage" type="success" class="mt-4">
      {{ cleanupMessage }}
    </v-alert>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      cleanupMessage: ''
    }
  },
  methods: {
    goToRegister() {
      this.$router.push('/register')
    },
    async runCleanup() {
      try {
        const response = await axios.post('http://localhost:5000/api/run-retention-cleanup')
        this.cleanupMessage = response.data.message
      } catch (error) {
        console.error('Cleanup failed', error)
        this.cleanupMessage = 'Failed to trigger cleanup task.'
      }
    }
  }
}
</script> -->


<!-- <template>
  <v-container>
    <h2>HRMS Dashboard</h2>

    <v-alert type="info" v-if="pendingCount > 0" class="mt-4">
      ⚠️ You have {{ pendingCount }} pending Data Rights Requests.
      <v-btn text--black @click="goToDSRDashboard">Review Now</v-btn>
    </v-alert>

    <v-btn color="primary" class="mt-4" @click="goToRegister">
      Register New Employee
    </v-btn>

    <v-btn color="error" class="mt-4 ml-2" @click="runCleanup">
      Run Retention Cleanup
    </v-btn>

    <v-btn color="secondary" class="mt-4 ml-2" @click="goToDSRRequest">
      Submit Data Rights Request
    </v-btn>

    <v-alert v-if="cleanupMessage" type="success" class="mt-4">
      {{ cleanupMessage }}
    </v-alert>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      cleanupMessage: '',
      pendingCount: 0
    }
  },
  methods: {
    goToRegister() {
      this.$router.push('/register')
    },
    async runCleanup() {
      try {
        const response = await axios.post('http://localhost:5000/api/run-retention-cleanup')
        this.cleanupMessage = response.data.message
      } catch (error) {
        console.error('Cleanup failed', error)
        this.cleanupMessage = 'Failed to trigger cleanup task.'
      }
    },
    async fetchDSRCount() {
      const res = await axios.get('http://localhost:5000/api/dsr-requests/count')
      this.pendingCount = res.data.pending_requests
    },
    goToDSRDashboard() {
      this.$router.push('/dsr-dashboard')
    },

    goToDSRRequest() {
      this.$router.push('/dsr-request')
    }
  },
  mounted() {
    this.fetchDSRCount()
  }
}
</script> -->


<!-- <template>
  <v-container>
    <h2>HRMS Dashboard</h2>

    <v-btn color="primary" class="mt-4" @click="goToRegister">
      Register New Employee
    </v-btn>

    <v-alert v-if="cleanupMessage" type="success" class="mt-4">
      {{ cleanupMessage }}
    </v-alert>

    <h3 class="mt-6">Employee Document Notifications</h3>

    <v-alert
      v-for="notification in notifications"
      :key="notification.id"
      type="info"
      class="mt-2"
    >
      📩 {{ notification.message }} — <small>{{ notification.created_at }}</small>
    </v-alert>

  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      cleanupMessage: '',
      pendingCount: 0,
      notifications: []
    }
  },
  mounted() {
    this.fetchNotifications()
  },
  methods: {
    goToRegister() {
      this.$router.push('/register')
    },
    async runCleanup() {
      try {
        const response = await axios.post('http://localhost:5000/api/run-retention-cleanup')
        this.cleanupMessage = response.data.message
      } catch (error) {
        console.error('Cleanup failed', error)
        this.cleanupMessage = 'Failed to trigger cleanup task.'
      }
    },
    goToDSRDashboard() {
      this.$router.push('/dsr-dashboard')
    },
    goToDSRRequest() {
      this.$router.push('/dsr-request')
    },
    async fetchNotifications() {
      try {
        const response = await axios.get('http://localhost:5000/api/notifications')
        this.notifications = response.data
      } catch (error) {
        console.error('Failed to fetch notifications', error)
      }
    }
  }
}
</script> -->


<!-- <template>
  <v-container>
    <v-app-bar flat app color="white">
      <v-toolbar-title>HRMS Dashboard</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="showNotifications = true">
        <v-icon>mdi-bell</v-icon>
        <v-badge v-if="unreadCount > 0" color="red" overlap dot></v-badge>
      </v-btn>
    </v-app-bar>

    <v-container>
      <h2>Welcome HR</h2>

      <v-btn color="primary" class="mt-4" @click="goToRegister">
        Register New Employee
      </v-btn>

      <v-alert v-if="cleanupMessage" type="success" class="mt-4">
        {{ cleanupMessage }}
      </v-alert>

      <v-data-table
        :headers="employeeHeaders"
        :items="employees"
        class="mt-6"
        dense
        :items-per-page="5"
        no-data-text="No employees found."
      >
        <template #item.pan_path="{ item }">
          <span v-if="item.pan_path">{{ item.pan_path }}</span>
          <span v-else>-</span>
        </template>
        <template #item.aadhaar_path="{ item }">
          <span v-if="item.aadhaar_path">{{ item.aadhaar_path }}</span>
          <span v-else>-</span>
        </template>
      </v-data-table>

      <v-dialog v-model="showNotifications" max-width="600">
        <v-card>
          <v-card-title>Notifications</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-alert
              v-for="notif in notifications"
              :key="notif.id"
              :type="'info'"
              :color="notif.is_read ? 'grey lighten-3' : 'blue lighten-4'"
              class="mb-2"
              @click="handleNotificationClick(notif)"
              style="cursor: pointer"
            >
              {{ notif.message }} <br />
              <small>{{ notif.created_at }}</small>
            </v-alert>
            <v-alert v-if="notifications.length === 0" type="info">
              No notifications.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>
  </v-container>
</template>

<script>
import axios from 'axios'
import { io } from 'socket.io-client'

export default {
  data() {
    return {
      cleanupMessage: '',
      pendingCount: 0,
      notifications: [],
      employees: [],
      showNotifications: false,
      socket: null,
      employeeHeaders: [
        { title: 'Name', value: 'name' },
        { title: 'Email', value: 'email' },
        { title: 'Department', value: 'department' },
        { title: 'PAN Path', value: 'pan_path' },
        { title: 'Aadhaar Path', value: 'aadhaar_path' }
      ]
    }
  },
  computed: {
    unreadCount() {
      return this.notifications.filter(n => !n.is_read).length
    }
  },
  mounted() {
    this.fetchNotifications()
    this.fetchEmployees()

    this.socket = io('http://localhost:5000')

    this.socket.on('new_notification', notif => {
      this.notifications.unshift(notif)
    })
  },
  methods: {
    goToRegister() {
      this.$router.push('/register')
    },
    async runCleanup() {
      try {
        const res = await axios.post('http://localhost:5000/api/run-retention-cleanup')
        this.cleanupMessage = res.data.message
      } catch (error) {
        console.error('Cleanup failed', error)
      }
    },
    async fetchNotifications() {
      try {
        const res = await axios.get('http://localhost:5000/api/notifications')
        this.notifications = res.data
      } catch (err) {
        console.error('Failed fetching notifications', err)
      }
    },
    async fetchEmployees() {
      try {
        const res = await axios.get('http://localhost:5000/api/employees')
        this.employees = res.data
      } catch (err) {
        console.error('Failed fetching employees', err)
      }
    },
    async handleNotificationClick(notif) {
      if (!notif.is_read) {
        await axios.post(`http://localhost:5000/api/notifications/${notif.id}/mark-read`)

        if (notif.type === 'document_submission') {
          await axios.post(`http://localhost:5000/api/send-consent/${notif.employee_id}`)
          alert('Consent request sent to employee.')
        } else if (notif.type === 'consent_given') {
          await axios.post(`http://localhost:5000/api/send-final-email/${notif.employee_id}`)
          alert('Final email with NDA and offer letter sent to employee.')
        }

        this.fetchNotifications()
      }
      this.showNotifications = false
    }
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect()
    }
  }
}
</script>-->

<!-- <template>
  <v-container>
    <v-app-bar flat app color="white">
      <v-toolbar-title>HRMS Dashboard</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="showNotifications = true">
        <v-icon>mdi-bell</v-icon>
        <v-badge v-if="unreadCount > 0" color="red" overlap dot></v-badge>
      </v-btn>
    </v-app-bar>

    <v-container>
      <h2>Welcome HR</h2>

      <v-btn color="primary" class="mt-4" @click="goToRegister">
        Register New Employee
      </v-btn>

      <v-btn color="secondary" class="mt-4 ml-4" @click="goToRetentionLogs">
        View Retention Logs
      </v-btn>

      <v-btn color="error" class="mt-4 ml-4" @click="runCleanup">
        Run Retention Cleanup
      </v-btn>

      <v-alert v-if="cleanupMessage" type="success" class="mt-4">
        {{ cleanupMessage }}
      </v-alert>

      <v-data-table
        :headers="employeeHeaders"
        :items="employees"
        class="mt-6"
        dense
        :items-per-page="5"
        no-data-text="No employees found."
      >
        <template #item.pan_path="{ item }">
          <span v-if="item.pan_path">{{ item.pan_path }}</span>
          <span v-else>-</span>
        </template>
        <template #item.aadhaar_path="{ item }">
          <span v-if="item.aadhaar_path">{{ item.aadhaar_path }}</span>
          <span v-else>-</span>
        </template>
        <template #item.actions="{ item }">
          <v-btn small color="error" @click="deleteDocuments(item.id)">
            Delete Docs
          </v-btn>
        </template>
      </v-data-table>

      <v-dialog v-model="showNotifications" max-width="600">
        <v-card>
          <v-card-title>Notifications</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-alert
              v-for="notif in notifications"
              :key="notif.id"
              :type="'info'"
              :color="notif.is_read ? 'grey lighten-3' : 'blue lighten-4'"
              class="mb-2"
              @click="handleNotificationClick(notif)"
              style="cursor: pointer"
            >
              {{ notif.message }} <br />
              <small>{{ notif.created_at }}</small>
            </v-alert>
            <v-alert v-if="notifications.length === 0" type="info">
              No notifications.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>
  </v-container>
</template>

<script>
import axios from 'axios'
import { io } from 'socket.io-client'

export default {
  data() {
    return {
      cleanupMessage: '',
      notifications: [],
      employees: [],
      showNotifications: false,
      socket: null,
      employeeHeaders: [
        { title: 'Name', value: 'name' },
        { title: 'Email', value: 'email' },
        { title: 'Department', value: 'department' },
        { title: 'PAN Path', value: 'pan_path' },
        { title: 'Aadhaar Path', value: 'aadhaar_path' },
        { title: 'Actions', value: 'actions', sortable: false }
      ]
    }
  },
  computed: {
    unreadCount() {
      return this.notifications.filter(n => !n.is_read).length
    }
  },
  mounted() {
    this.fetchNotifications()
    this.fetchEmployees()

    this.socket = io('http://localhost:5000')
    this.socket.on('new_notification', notif => {
      this.notifications.unshift(notif)
    })
  },
  methods: {
    goToRegister() {
      this.$router.push('/register')
    },
    goToRetentionLogs() {
      this.$router.push('/retention-logs')
    },
    async runCleanup() {
      try {
        const res = await axios.post('http://localhost:5000/api/run-retention-cleanup')
        this.cleanupMessage = res.data.message
      } catch (error) {
        console.error('Cleanup failed', error)
      }
    },
    async fetchNotifications() {
      try {
        const res = await axios.get('http://localhost:5000/api/notifications')
        this.notifications = res.data
      } catch (err) {
        console.error('Failed fetching notifications', err)
      }
    },
    async fetchEmployees() {
      try {
        const res = await axios.get('http://localhost:5000/api/employees')
        this.employees = res.data
      } catch (err) {
        console.error('Failed fetching employees', err)
      }
    },
    async handleNotificationClick(notif) {
      if (!notif.is_read) {
        await axios.post(`http://localhost:5000/api/notifications/${notif.id}/mark-read`)

        if (notif.type === 'document_submission') {
          await axios.post(`http://localhost:5000/api/send-consent/${notif.employee_id}`)
          alert('Consent request sent to employee.')
        } else if (notif.type === 'consent_given') {
          await axios.post(`http://localhost:5000/api/send-final-email/${notif.employee_id}`)
          alert('Final email with NDA and offer letter sent to employee.')
        }

        this.fetchNotifications()
      }
      this.showNotifications = false
    },

    async deleteDocuments(empId) {
      if (confirm("Are you sure you want to delete this employee and their documents?")) {
        try {
          await axios.post(`http://localhost:5000/api/employees/${empId}/delete-documents`)
          alert('Employee and documents deleted.')
          this.fetchEmployees()
        } catch (error) {
          console.error('Failed to delete employee', error)
          alert('Failed to delete employee.')
        }
      }
    }
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect()
    }
  }
}
</script> -->


<!-- src/views/AdminDashboard.vue -->
<!-- <template>
  <v-container>
    <div class="d-flex justify-end">
      <v-menu offset-y>
        <template #activator="{ props }">
          <v-badge dot color="red" v-if="unread">
            <v-btn icon v-bind="props">
              <v-icon>mdi-bell</v-icon>
            </v-btn>
          </v-badge>
          <v-btn icon v-bind="props" v-else>
            <v-icon>mdi-bell-outline</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item
            v-for="(note, index) in notifications"
            :key="index"
            @click="sendConsentAndRemove(index)"
          >
            <v-list-item-title>{{ note.message }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
    <h2 class="mb-4">Consent Management</h2>

    <v-btn color="primary" class="mr-2" @click="toggleEmployeeForm">
      {{ showEmployeeForm ? 'Close Employee Form' : 'Add Employee' }}
    </v-btn>

    <v-btn color="secondary" @click="togglePurposeForm">
      {{ showPurposeForm ? 'Close Purpose Form' : 'Add Purpose' }}
    </v-btn>

    <v-expand-transition>
      <div v-if="showEmployeeForm" class="mt-4">
        <EmployeeForm @employee-added="handleEmployeeAdded" />
      </div>
    </v-expand-transition>

    <v-expand-transition>
      <div v-if="showPurposeForm" class="mt-4">
        <PurposeForm @purpose-added="handlePurposeAdded" />
      </div>
    </v-expand-transition>

    <EmployeeTable :employees="employees" class="mt-5" />

    <v-snackbar v-model="snackbar" :timeout="5000" color="success">
      {{ snackbarMessage }}
    </v-snackbar>

    <v-alert
      v-for="notif in notifications"
      :key="notif.id"
      type="info"
      border="left"
      elevation="2"
      class="mt-3"
      @click="sendConsentEmail(notif.emp_id)"
      style="cursor: pointer"
    >
      Documents uploaded by {{ notif.name }} — Click to send consent form
    </v-alert>
  </v-container>
</template>

<script>
import EmployeeForm from '@/components/EmployeeForm.vue'
import PurposeForm from '@/components/PurposeForm.vue'
import EmployeeTable from '@/components/EmployeeTable.vue'
import axios from 'axios'
import { io } from 'socket.io-client'

export default {
  components: {
    EmployeeForm,
    PurposeForm,
    EmployeeTable
  },
  data() {
    return {
      employees: [],
      showEmployeeForm: false,
      showPurposeForm: false,
      notifications: [],
      unread: false
    }
  },

  mounted() {
  this.loadEmployees();

  const socket = io('http://localhost:5000');

  socket.on('document_uploaded', (data) => {
    this.notifications.unshift({
      message: `📄 Documents uploaded by ${data.employee_name}`,
      employeeId: data.employee_id,
      type: 'document_uploaded'
    });
    this.unread = true;
  });

  socket.on('consent_submitted', (data) => {
    this.notifications.unshift({
      message: `✅ Consent submitted by ${data.employee_name}`,
      employeeId: data.employee_id,
      type: 'consent_submitted'
    });
    this.unread = true;
  });
},

  methods: {
    loadEmployees() {
      axios.get('http://127.0.0.1:5000/api/employees').then(res => {
        this.employees = res.data
      })
    },
    toggleEmployeeForm() {
      this.showEmployeeForm = !this.showEmployeeForm
      if (this.showEmployeeForm) this.showPurposeForm = false
    },
    togglePurposeForm() {
      this.showPurposeForm = !this.showPurposeForm
      if (this.showPurposeForm) this.showEmployeeForm = false
    },
    handleEmployeeAdded() {
      this.loadEmployees()
      this.showEmployeeForm = false
    },
    handlePurposeAdded() {
      this.showPurposeForm = false
    },
    async sendConsentAndRemove(index) {
  const notification = this.notifications[index];
  const empId = notification.employeeId;

  if (notification.type === 'document_uploaded') {
    // Send consent mail
    try {
      await axios.post(`http://127.0.0.1:5000/api/employees/${empId}/send-consent`);
      this.notifications.splice(index, 1);
      if (this.notifications.length === 0) this.unread = false;
      this.$vuetify.snackbar = {
        color: 'success',
        timeout: 4000,
        message: 'Consent email sent successfully.'
      };
    } catch (error) {
      this.$vuetify.snackbar = {
        color: 'error',
        timeout: 4000,
        message: 'Failed to send consent email.'
      };
    }
  }

  // Future: handle consent_submitted → send final email (offer letter + NDA)
},


     markAsRead(index) {
      this.notifications.splice(index, 1)
      this.unreadCount = Math.max(0, this.unreadCount - 1)
    }
  },
}
</script> -->


<template>
  <v-container>
    <!-- Your existing dashboard content -->
    <div class="d-flex justify-end mb-4">
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-badge :content="unreadCount" :value="unreadCount > 0" color="red">
              <v-icon>mdi-bell</v-icon>
            </v-badge>
          </v-btn>
        </template>

        <v-list style="min-width: 300px;">
          <v-list-item
            v-for="(note, idx) in notifications"
            :key="note.id"
            @click="handleNotificationClick(note, idx)"
            class="notification-item"
          >
            <v-list-item-title>{{ note.message }}</v-list-item-title>
            <v-list-item-subtitle>{{ note.created_at }}</v-list-item-subtitle>
          </v-list-item>

          <v-list-item v-if="notifications.length === 0">
            <v-list-item-title>No notifications</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>

    <!-- Rest of your dashboard content here -->
     <!-- <h2 class="mb-4">Consent Management</h2> -->

    <v-btn color="primary" class="mr-2" @click="toggleEmployeeForm">
      {{ showEmployeeForm ? 'Close Employee Form' : 'Add Employee' }}
    </v-btn>

    <!-- <v-btn color="secondary" @click="togglePurposeForm">
      {{ showPurposeForm ? 'Close Purpose Form' : 'Add Purpose' }}
    </v-btn> -->

    <!-- 🚀 New Training Page Button -->
    <v-btn color="success" @click="goToTraining">
      Go to Training Page
    </v-btn>

    <v-expand-transition>
      <div v-if="showEmployeeForm" class="mt-4">
        <EmployeeForm @employee-added="handleEmployeeAdded" />
      </div>
    </v-expand-transition>

    <v-expand-transition>
      <div v-if="showPurposeForm" class="mt-4">
        <PurposeForm @purpose-added="handlePurposeAdded" />
      </div>
    </v-expand-transition>

    <EmployeeTable :employees="employees" class="mt-5" />

    <v-snackbar v-model="snackbar" :timeout="5000" color="success">
      {{ snackbarMessage }}
    </v-snackbar>

    <!-- <v-alert
      v-for="notif in notifications"
      :key="notif.id"
      type="info"
      border="left"
      elevation="2"
      class="mt-3"
      @click="sendConsentEmail(notif.emp_id)"
      style="cursor: pointer"
    >
      Documents uploaded by {{ notif.name }} — Click to send consent form
    </v-alert> -->

    <v-dialog v-model="finalMailDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">Upload NDA & Offer Letter</v-card-title>
        <v-card-text>
          <!-- <v-file-input
            label="Upload NDA Agreement"
            accept=".pdf,.docx"
            @change="ndaFile = $event"
          ></v-file-input>
          <v-file-input
            label="Upload Offer Letter"
            accept=".pdf,.docx"
            @change="offerLetterFile = $event"
          ></v-file-input> -->
          <v-file-input
            v-model="ndaFile"
            label="Upload NDA Agreement"
            accept=".pdf,.docx"
          />

          <v-file-input
            v-model="offerLetterFile"
            label="Upload Offer Letter"
            accept=".pdf,.docx"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="submitFinalEmail">Submit</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script>
import EmployeeForm from '@/components/EmployeeForm.vue'
import PurposeForm from '@/components/PurposeForm.vue'
import EmployeeTable from '@/components/EmployeeTable.vue'
import axios from 'axios'
import { io } from 'socket.io-client'

export default {
  components: {
    EmployeeForm,
    PurposeForm,
    EmployeeTable
  },

  data() {
    return {
      employees: [],
      showEmployeeForm: false,
      showPurposeForm: false,
      notifications: [],
      unread: false,
      finalMailDialog: false,
      selectedEmployeeId: null,
      ndaFile: null,
      offerLetterFile: null
    }
  },
  computed: {
    unreadCount() {
      return this.notifications.filter(n => !n.is_read).length
    }
  },
  mounted() {
    this.loadEmployees();
    this.loadNotifications()

    // const socket = io('http://localhost:5000')
    const socket = io('https://hrms-4jys.onrender.com')
    socket.on('new_notification', (note) => {
      this.notifications.unshift(note)
      this.loadEmployees();
    })
  },
  methods: {
    loadEmployees() {
      // axios.get('http://127.0.0.1:5000/api/employees').then(res => {
      axios.get('https://hrms-4jys.onrender.com/api/employees').then(res => {
        this.employees = res.data
      })
    },
    toggleEmployeeForm() {
      this.showEmployeeForm = !this.showEmployeeForm
      if (this.showEmployeeForm) this.showPurposeForm = false
    },
    togglePurposeForm() {
      this.showPurposeForm = !this.showPurposeForm
      if (this.showPurposeForm) this.showEmployeeForm = false
    },
    handleEmployeeAdded() {
      this.loadEmployees()
      this.showEmployeeForm = false
    },
    handlePurposeAdded() {
      this.showPurposeForm = false
    },

    async loadNotifications() {
      // const res = await axios.get('http://127.0.0.1:5000/api/notifications')
      const res = await axios.get('https://hrms-4jys.onrender.com/api/notifications')
      this.notifications = res.data
    },
    async handleNotificationClick(note, index) {
      if (note.type === 'document_uploaded') {
        // First notification — send consent email
        await this.sendConsent(note.emp_id)
        this.loadEmployees()
      } else if (note.type === 'consent_submitted') {
        // Second notification — open final email dialog
        this.selectedEmployeeId = note.emp_id
        this.finalMailDialog = true
        this.loadEmployees()
      }

      // Mark notification as read and remove from UI
      // await axios.patch(`http://127.0.0.1:5000/api/notifications/${note.id}/read`)
      await axios.patch(`https://hrms-4jys.onrender.com/api/notifications/${note.id}/read`)
      this.notifications.splice(index, 1)
    },
    async sendConsent(empId) {
      // await axios.post(`http://127.0.0.1:5000/api/employees/${empId}/send-consent`)
      await axios.post(`https://hrms-4jys.onrender.com/api/employees/${empId}/send-consent`)
    },

    // async submitFinalEmail() {
    //   if (!this.ndaFile || !this.offerLetterFile) {
    //     alert('Please upload both NDA and Offer Letter')
    //     return
    //   }

    //   const formData = new FormData()
    //   formData.append('nda', this.ndaFile)
    //   formData.append('offer_letter', this.offerLetterFile)

    //   await axios.post(
    //     `http://127.0.0.1:5000/api/employees/${this.selectedEmployeeId}/send-final-email`,
    //     formData,
    //     { headers: { 'Content-Type': 'multipart/form-data' } }
    //   )

    //   this.finalMailDialog = false
    //   this.ndaFile = null
    //   this.offerLetterFile = null
    //   this.selectedEmployeeId = null
    // }

    async submitFinalEmail() {
      if (!this.ndaFile || !this.offerLetterFile) {
        alert('Please upload both NDA and Offer Letter');
        return;
      }

      const formData = new FormData();
      formData.append('nda', this.ndaFile);
      formData.append('offer_letter', this.offerLetterFile);

      await axios.post(
        // `http://127.0.0.1:5000/api/employees/${this.selectedEmployeeId}/send-final-email`,
        `https://hrms-4jys.onrender.com/api/employees/${this.selectedEmployeeId}/send-final-email`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      this.finalMailDialog = false;
      this.ndaFile = null;
      this.offerLetterFile = null;
      this.selectedEmployeeId = null;
    },
    goToTraining() {
      this.$router.push('/training') // 👈 assumes you have /training route in router.js
    }
  }
}
</script>

<style scoped>
.notification-item {
  cursor: pointer;
}
.notification-item:hover {
  background-color: #f5f5f5;
}
</style>