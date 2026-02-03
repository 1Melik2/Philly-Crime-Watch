[![NotificationAPI](./ReadmeLogo.svg)](https://notificationapi.com)

The React SDK is mainly used for displaying In-App Notifications, allowing users to see and change their Notification Preferences and enabling web push notification .

# Docs

Please refer to our [documentations](https://docs.notificationapi.com).

# Debug Mode

The SDK includes a comprehensive debug mode to help troubleshoot issues and understand SDK behavior. Enable it by adding the `debug` prop:

```jsx
<NotificationAPIProvider
  clientId="your-client-id"
  userId="your-user-id"
  debug={true}
>
  {/* Your app components */}
</NotificationAPIProvider>
```

For detailed information about debug mode, see [DEBUG.md](./DEBUG.md).

# Development

1. Install dependencies:

```
npm install
```

2. Run the example application:

```
npm run dev
```

The example application includes a debug mode toggle to demonstrate the feature.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default {
  // other rules...
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: ['./tsconfig.json', './tsconfig.node.json'],
    tsconfigRootDir: __dirname
  }
};
```

- Replace `plugin:@typescript-eslint/recommended` to `plugin:@typescript-eslint/recommended-type-checked` or `plugin:@typescript-eslint/strict-type-checked`
- Optionally add `plugin:@typescript-eslint/stylistic-type-checked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and add `plugin:react/recommended` & `plugin:react/jsx-runtime` to the `extends` list

## Contributing

We welcome contributions! To ensure smooth collaboration, please follow these steps:

1. **Clone the Repository**

   - Fork the repository to your GitHub account.
   - Clone it to your local machine:

     ```bash
     git clone https://github.com/your-username/repo-name.git
     cd repo-name
     ```

2. **Create a Branch**

   - Create a new branch for your changes:

     ```bash
     git checkout -b your-branch-name
     ```

3. **Make Your Changes**

   - Make your changes in the relevant files.
   - Thoroughly test your changes to ensure they work as expected.

4. **Versioning**

   - Before committing your changes, update the package version by running:

     ```bash
     npm version <type>
     ```

   - **Versioning Types:**

     - **major**: For breaking changes or large-scale features.
     - **minor**: For adding functionality in a backwards-compatible manner.
     - **patch**: For backwards-compatible bug fixes or small improvements.

   - For example, to update a patch version:

     ```bash
     npm version patch
     ```

5. **Commit and Push**

   - Once you've made and tested your changes, commit them with a meaningful message:

     ```bash
     git add .
     git commit -m "Describe your changes"
     ```

   - Push your branch to GitHub:

     ```bash
     git push origin your-branch-name
     ```

6. **Submit a Pull Request**

   - Create a pull request (PR) on GitHub.
   - Provide a clear description of what your changes do.
   - Link any relevant issues.

7. **Update Documentation**
   - If your changes affect the documentation, please update it accordingly.
   - You can find the documentation repository here: [NotificationAPI Docs](https://github.com/notificationapi-com/docs).

Thank you for contributing!
