<template>
  <div class="loginFormDiv">
    <form @submit.prevent="this.authenticate">
      <DxForm ref="loginForm" :form-data="this.loginFormData">
        <DxGroupItem caption="Авторизация">
          <DxGroupItem>
            <DxSimpleItem data-field="username">
              <DxLabel text="Логин" />
              <DxRequiredRule message="Введите логин" />
            </DxSimpleItem>
            <DxSimpleItem data-field="password" :editor-options="this.passwordEditorOptions">
              <DxLabel text="Пароль" />
              <DxRequiredRule message="Введите пароль" />
            </DxSimpleItem>
          </DxGroupItem>
          <DxButtonItem :button-options="this.enterButtonOptions" />
          <DxButtonItem :button-options="this.registerButtonOptions" />
        </DxGroupItem>
      </DxForm>
    </form>
  </div>
</template>

<script>
import DxForm, {
  DxGroupItem,
  DxRequiredRule,
  DxSimpleItem,
  DxLabel,
  DxButtonItem
} from 'devextreme-vue/form'
import axios from 'axios'
import notify from 'devextreme/ui/notify'

export default {
  components: {
    DxForm,
    DxGroupItem,
    DxSimpleItem,
    DxRequiredRule,
    DxLabel,
    DxButtonItem
  },
  data() {
    return {
      passwordEditorOptions: {
        mode: 'password'
      },
      enterButtonOptions: {
        text: 'Войти',
        type: 'default',
        width: '500px',
        useSubmitBehavior: true
      },
      registerButtonOptions: {
        text: 'Регистрация',
        type: 'default',
        width: '500px',
        onClick: this.register
      },
      loginFormData: {
        username: null,
        password: null
      }
    }
  },
  methods: {
    authenticate() {
      const User = new FormData()
      User.append('username', this.loginFormData.username)
      User.append('password', this.loginFormData.password)
      axios
        .post('/auth/sign-in', User)
        .then((res) => {
          this.$store.dispatch('authenticateUser', res.data.access_token)
          this.$router.push('/')
        })
        .catch((error) => {
          notify({ message: error.response.data.detail, type: 'error' }, { position: 'center' })
        })
    },
    register() {
      this.$router.push('/register')
    }
  }
}
</script>

<style scoped>
.loginFormDiv {
  margin: auto;
  width: 350px;
  margin-top: 15px;
  border: 1px solid #d1d1d1;
  padding: 15px;
}
</style>
