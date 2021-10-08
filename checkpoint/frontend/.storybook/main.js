module.exports = {
  webpackFinal: async (config, { configType }) => {
    config.module.rules.push({
      test: /.*\.less$/,
      loaders: [
        'style-loader',
        'css-loader',
        {
            loader: "less-loader",
            options: {
                lessOptions: {
                    javascriptEnabled: true
                }
            }
        },
      ]
    });
    return config;
  },
  "stories": ["../src/**/*.stories.tsx"],
  "addons": [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    {
      "name": "@storybook/preset-create-react-app",
      "options": {
        "craOverrides": {
          "fileLoaderExcludes": ["less"]
        }
      }
    }
  ]
}
