import type { Meta, StoryObj } from '@storybook/react';
import { BudgetCard } from './BudgetCard';

const meta: Meta<typeof BudgetCard> = {
  title: 'Components/BudgetCard',
  component: BudgetCard,
  argTypes: {
    status: { control: 'inline-radio', options: ['on-track', 'near-limit', 'over'] },
    percentUsed: { control: { type: 'range', min: 0, max: 100, step: 1 } },
  },
};

export default meta;

type Story = StoryObj<typeof BudgetCard>;

export const OnTrack: Story = {
  args: {
    label: 'Groceries',
    spentLabel: '$420',
    limitLabel: '$600',
    percentUsed: 70,
    status: 'on-track',
    statusLabel: '$180 left',
  },
};

export const NearLimit: Story = {
  args: {
    label: 'Dining out',
    spentLabel: '$185',
    limitLabel: '$200',
    percentUsed: 93,
    status: 'near-limit',
    statusLabel: '$15 left',
  },
};

export const OverBudget: Story = {
  args: {
    label: 'Transport',
    spentLabel: '$162',
    limitLabel: '$150',
    percentUsed: 100,
    status: 'over',
    statusLabel: '$12 over',
  },
};
