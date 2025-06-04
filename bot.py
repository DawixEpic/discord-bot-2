require('dotenv').config();
const { Client, GatewayIntentBits, Partials, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.MessageContent
  ],
  partials: [Partials.Message, Partials.Channel, Partials.Reaction],
});

const CHANNEL_ID = '1373258480382771270';
const ROLE_ID = '1373275307150278686';
const BUTTON_ID = 'verify_button';

client.once('ready', async () => {
  console.log(`Zalogowano jako ${client.user.tag}`);

  const channel = await client.channels.fetch(CHANNEL_ID);
  if (!channel.isTextBased()) return;

  // Usuwanie wszystkich wiadomości
  const messages = await channel.messages.fetch({ limit: 100 });
  await Promise.all(messages.map(msg => msg.delete()));

  // Tworzenie wiadomości z przyciskiem
  const row = new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(BUTTON_ID)
      .setLabel('✅ Zweryfikuj się')
      .setStyle(ButtonStyle.Success)
  );

  await channel.send({
    content: '**Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.**',
    components: [row]
  });
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isButton()) return;
  if (interaction.customId !== BUTTON_ID) return;

  const role = interaction.guild.roles.cache.get(ROLE_ID);
  const member = interaction.member;

  if (member.roles.cache.has(ROLE_ID)) {
    await interaction.reply({ content: 'Masz już tę rolę.', ephemeral: true });
  } else {
    await member.roles.add(role);
    await interaction.reply({ content: '✅ Pomyślnie zweryfikowano i nadano rolę!', ephemeral: true });
  }
});

client.login(process.env.DISCORD_TOKEN);
