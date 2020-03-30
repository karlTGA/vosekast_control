module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "react"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/eslint-recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "prettier",
    "prettier/react",
    "prettier/@typescript-eslint"
  ],
  env: {
    browser: true
  },
  rules: {
    "linebreak-style": "off",
    "react/prefer-stateless-function": 1,
    "require-jsdoc": 0,
    "valid-jsdoc": 0,
    "no-invalid-this": 0,
    "@typescript-eslint/camelcase": 1,
    "@typescript-eslint/no-unused-vars": ["error", { args: "none" }],
    "@typescript-eslint/no-empty-function": 1,
    "@typescript-eslint/no-var-requires": 1,
    "@typescript-eslint/no-use-before-define": 0,
    "@typescript-eslint/ban-types": 1,
    "@typescript-eslint/no-inferrable-types": [
      "warn",
      { ignoreParameters: true, ignoreProperties: true }
    ],
    "@typescript-eslint/explicit-function-return-type": 0,
    eqeqeq: ["error", "smart"]
  },
  settings: {
    react: {
      version: "16.13"
    }
  }
};
