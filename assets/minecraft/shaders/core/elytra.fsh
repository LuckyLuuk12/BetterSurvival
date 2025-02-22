#version 150
uniform sampler2D texture;

void main() {
    vec4 color = texture2D(texture, gl_TexCoord[0].st);
    gl_FragColor = vec4(color.rgb, color.a); // Use the alpha value from the texture
}