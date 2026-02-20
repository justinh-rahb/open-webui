// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />

describe('Embed', () => {
	it('allows public embed route without auth redirect', () => {
		cy.visit('/embed/test-panel');
		cy.url().should('include', '/embed/test-panel');
		cy.contains('Waiting for authentication...').should('exist');
	});
});
